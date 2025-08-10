FROM public.ecr.aws/lambda/python:3.12
COPY requirements.txt .
RUN python -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY app/ ${LAMBDA_TASK_ROOT}/
CMD ["handler.main"]
