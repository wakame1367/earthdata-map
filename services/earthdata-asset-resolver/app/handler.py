import json, os
import boto3, requests
from urllib.parse import urlparse

SECRETS_ARN = os.environ["EDL_SECRET_ARN"]
REGION = os.environ.get("AWS_REGION", "us-west-2")

DAAC_S3CREDS = {
  "LPDAAC": os.environ.get("DAAC_LPDAAC_S3CRED", "https://data.lpdaac.earthdatacloud.nasa.gov/s3credentials")
}

sm = boto3.client("secretsmanager", region_name=REGION)

def _get_edl_token():
  sec = sm.get_secret_value(SecretId=SECRETS_ARN)
  return json.loads(sec["SecretString"])["token"]  # 60日/同時2個まで。:contentReference[oaicite:11]{index=11}

def _get_s3_creds(edl_token: str, provider_key: str):
  url = DAAC_S3CREDS[provider_key]
  r = requests.get(url, headers={"Authorization": f"Bearer {edl_token}"}, timeout=15)
  r.raise_for_status()
  return r.json()  # accessKeyId/secretAccessKey/sessionToken/expiration（~1h）:contentReference[oaicite:12]{index=12}

def _presign_s3(s3url: str, temp: dict):
  p = urlparse(s3url)  # s3://bucket/key
  s3 = boto3.client("s3",
    region_name=REGION,
    aws_access_key_id=temp["accessKeyId"],
    aws_secret_access_key=temp["secretAccessKey"],
    aws_session_token=temp["sessionToken"])
  return s3.generate_presigned_url("get_object",
    Params={"Bucket": p.netloc, "Key": p.path.lstrip("/")}, ExpiresIn=900)

def main(event, context):
  body = json.loads(event.get("body") or "{}")
  item_href, asset_key = body["itemHref"], body["assetKey"]

  item = requests.get(item_href, timeout=20).json()
  href = item["assets"][asset_key]["href"]

  if href.startswith("s3://"):
    token = _get_edl_token()
    temp  = _get_s3_creds(token, "LPDAAC")
    url   = _presign_s3(href, temp)
    return _resp(200, {"url": url, "method": "s3-presign"})
  elif href.startswith("https://"):
    # 公開HTTP or 別途プロキシ（EDL必要なら将来拡張）
    return _resp(200, {"url": href, "method": "public"})
  else:
    return _resp(400, {"error": "Unsupported href"})

def _resp(code, obj):
  return {"statusCode": code, "headers": {"content-type":"application/json"}, "body": json.dumps(obj)}
