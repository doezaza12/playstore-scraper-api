FROM --platform=linux/amd64 python:3.9-slim

COPY ./ ./

RUN pip install -r requirements.txt

ENV PORT=8000 \
    LOG_LEVEL=DEBUG \
    LAMBDA_FUNCTION_NAME=lambda-eip-switching \
    REGION=ap-southeast-1 \
    THROTTLING=200

EXPOSE ${PORT}

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]