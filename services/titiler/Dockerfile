# Lambda (Python 3.12 / AL2023) 公式ベース
FROM public.ecr.aws/lambda/python:3.12

# 推奨: GDAL/Raster 読み込みの安定化/チューニング
ENV GDAL_CACHEMAX=256 \
    VSI_CACHE=TRUE \
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff,.img,.vrt,.jp2,.png,.jpg,.jpeg,.zip,.gz"

# 依存をまとめて入れる
COPY requirements.txt .
RUN python -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY app/ ${LAMBDA_TASK_ROOT}/
CMD [ "handler.handler" ]
