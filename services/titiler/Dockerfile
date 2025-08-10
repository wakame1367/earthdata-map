# Lambda (Python 3.12 / AL2023) 公式ベース
FROM public.ecr.aws/lambda/python:3.12

# 推奨: GDAL/Raster 読み込みの安定化/チューニング
ENV GDAL_CACHEMAX=256 \
    VSI_CACHE=TRUE \
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff,.img,.vrt,.jp2,.png,.jpg,.jpeg,.zip,.gz"

# 依存をまとめて入れる
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体
COPY app.py ${LAMBDA_TASK_ROOT}/

# Lambda ハンドラ指定（app.py の handler）
CMD [ "app.handler" ]
