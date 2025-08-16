import os, json, urllib.parse, datetime as dt
import boto3, requests
from botocore.session import Session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from urllib.parse import urlparse

# === env ===
TITILER_BASE = os.environ["TITILER_BASE"]
REGION       = os.environ.get("AWS_REGION", "us-west-2")
EDL_SECRET_ID= os.environ["EDL_SECRET_ID"]
DAAC_S3CREDS = os.environ.get("DAAC_LPDAAC_S3CRED", "https://data.lpdaac.earthdatacloud.nasa.gov/s3credentials")
CMR_STAC     = os.environ.get("CMR_STAC", "https://cmr.earthdata.nasa.gov/stac")
PROVIDER_ID  = os.environ.get("PROVIDER_ID", "LPCLOUD")  # LP DAAC のクラウド資産
DEFAULT_TMS  = os.environ.get("DEFAULT_TMS", "WebMercatorQuad")

sm = boto3.client("secretsmanager", region_name=REGION)

def _resp(code, obj):
    return {"statusCode": code, "headers": {"content-type":"application/json"}, "body": json.dumps(obj)}

def _parse_http_event(event):
    if isinstance(event, str):
        try: return json.loads(event)
        except: return {}
    if isinstance(event, dict) and "body" in event:
        body = event["body"]
        if isinstance(body, str):
            if event.get("isBase64Encoded"):
                import base64; body = base64.b64decode(body).decode("utf-8")
            try: return json.loads(body)
            except: return {}
        return body or {}
    return event if isinstance(event, dict) else {}

def _edl_token():
    sec = sm.get_secret_value(SecretId=EDL_SECRET_ID)
    return json.loads(sec["SecretString"])["token"]

def _lpdaac_s3creds(edl_token: str):
    r = requests.get(DAAC_S3CREDS, headers={"Authorization": f"Bearer {edl_token}"}, timeout=20)
    r.raise_for_status()
    return r.json()  # accessKeyId/secretAccessKey/sessionToken/expiration

def _presign_s3(s3url: str, temp: dict, expires=900):
    p = urlparse(s3url)  # s3://bucket/key
    s3 = boto3.client("s3",
        region_name=REGION,  # Earthdata Cloud は us-west-2
        aws_access_key_id=temp["accessKeyId"],
        aws_secret_access_key=temp["secretAccessKey"],
        aws_session_token=temp["sessionToken"])
    return s3.generate_presigned_url("get_object",
        Params={"Bucket": p.netloc, "Key": p.path.lstrip("/")}, ExpiresIn=expires)

def _signed_get(url: str):
    # API Gateway(HTTP API) を IAM 署名で GET
    sess = Session()
    cre = sess.get_credentials().get_frozen_credentials()
    req = AWSRequest(method="GET", url=url)
    SigV4Auth(cre, "execute-api", REGION).add_auth(req)
    preq = requests.Request("GET", url, headers=dict(req.headers)).prepare()
    return requests.Session().send(preq, timeout=30)

def handler(event, context):
    data = _parse_http_event(event)
    # 入力: date(YYYY-MM-DD), bbox[minx,miny,maxx,maxy], collection(任意), assetKey(任意), renderパラメータ(任意)
    date    = data.get("date")            # 例 "2025-08-13"
    bbox    = data.get("bbox")            # 例 [minx,miny,maxx,maxy]
    colls   = data.get("collections")     # 例 ["HLSL30.v1.5"]
    asset   = data.get("assetKey")        # 例 "B04" / "data"
    render  = data.get("render", {})      # 例 {"rescale":"0,3000","colormap_name":"cfastie"}
    use_stac= bool(data.get("useStac", False))  # item URL を /stac で処理したい場合

    if not (date and bbox and isinstance(bbox, (list, tuple)) and len(bbox) == 4):
        return _resp(400, {"error":"date(YYYY-MM-DD) と bbox[minx,miny,maxx,maxy] は必須"})

    # STAC datetime（UTC の1日幅）。UI から UTC で来るならそのまま interval を渡す設計でもOK
    start = f"{date}T00:00:00Z"
    end   = f"{date}T23:59:59Z"
    dt_param = f"{start}/{end}"

    # CMR-STAC 検索（GET /{provider}/search?bbox=&datetime=&limit=&collections=...）
    qs = {
        "bbox": ",".join(map(str, bbox)),
        "datetime": dt_param,
        "limit": "1"
    }
    if colls: qs["collections"] = ",".join(colls)

    search_url = f"{CMR_STAC}/{PROVIDER_ID}/search"
    sr = requests.get(search_url, params=qs, timeout=30)
    if sr.status_code != 200:
        return _resp(502, {"error":"STAC search failed", "detail": sr.text})
    items = sr.json().get("features", [])
    if not items:
        return _resp(404, {"error":"No STAC items", "query": {"bbox": bbox, "datetime": dt_param, "collections": colls}})

    item = items[0]  # 最初の1件
    item_href = next((l["href"] for l in item.get("links", []) if l.get("rel") in ("self","canonical") and l.get("type","").endswith("json")), None)
    if not item_href:
        return _resp(502, {"error":"Item href not found"})

    # アセット選択
    assets = item.get("assets", {})
    if asset and asset in assets:
        href = assets[asset]["href"]
    else:
        # assetKey 未指定なら 最初の raster/COG らしいものを当てる
        cand = [a["href"] for a in assets.values() if isinstance(a, dict) and "href" in a]
        if not cand: return _resp(502, {"error":"No asset href in item"})
        href = cand[0]

    # 解決: s3:// は LPDAAC s3credentials → S3 presign, https はそのまま
    if href.startswith("s3://"):
        token = _edl_token()
        temp  = _lpdaac_s3creds(token)
        cog_url = _presign_s3(href, temp)
    else:
        cog_url = href  # 公開 HTTPS or 別 DAAC の公開配信

    # TiTiler tilejson 取得
    if use_stac:
        # /stac/{TMS}/tilejson.json?url=item.json&assets=... でアセット名を指定
        tj_qs = {
            "url": item_href,
        }
        if asset: tj_qs["assets"] = asset
        tj_qs.update({k:v for k,v in render.items() if v is not None})
        url = f"{TITILER_BASE}/stac/{DEFAULT_TMS}/tilejson.json?{urllib.parse.urlencode(tj_qs, doseq=True)}"
    else:
        # /cog/tilejson.json?url=COG_URL
        # 署名URLの & 衝突を避けるため、value は URL エンコード
        tj_qs = {"url": cog_url}
        tj_qs.update({k:v for k,v in render.items() if v is not None})
        url = f"{TITILER_BASE}/cog/tilejson.json?{urllib.parse.urlencode(tj_qs, doseq=True)}"

    tr = _signed_get(url)  # IAM 認可の TiTiler に署名付きでアクセス
    if tr.status_code != 200:
        return _resp(502, {"error":"TiTiler tilejson failed", "detail": tr.text})

    tilejson = tr.json()
    return _resp(200, {
        "tilejson": tilejson,
        "provenance": {
            "provider": PROVIDER_ID,
            "query": {"bbox": bbox, "datetime": dt_param, "collections": colls, "assetKey": asset},
            "item": {"id": item.get("id"), "datetime": item.get("properties",{}).get("datetime"), "href": item_href}
        }
    })
