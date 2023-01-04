import os
import logging
import boto3
from functools import wraps
from logging.config import fileConfig
from fastapi import FastAPI, Response, status
from google_play_scraper import search
from google_play_scraper.exceptions import ExtraHTTPError, NotFoundError

fileConfig('logging.conf')
lambda_client = boto3.client('lambda', region_name=os.getenv('REGION', 'ap-southeast-1'))
THROTTLING = int(os.getenv('THROTTLING', 100))
LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME')
app = FastAPI()


def throttling(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        counter = int(os.getenv('COUNTER', 0)) + 1
        # handle throttling
        if counter > THROTTLING:
            # invoke lambda to swap EIP
            lambda_client.invoke(
                FunctionName=LAMBDA_FUNCTION_NAME,
                InvocationType='RequestResponse'
            )
            os.environ['COUNTER'] = str(0)
            logging.info(f'reset throttling')
        else:
            os.environ['COUNTER'] = str(counter)

        logging.info(f'requests count: {counter}')

        return await func(*args, **kwargs)
    return wrapper


@app.get('/')
async def healthcheck():
    return {'message': 'I\'m healthy'}


@app.get('/{app_name}')
@throttling
async def get_appstore_app_by_name(app_name: str, response: Response):
    try:
        resp = search(f'{app_name}', n_hits=1)
        logging.info(f'GET /{app_name} {status.HTTP_200_OK} OK')

    except NotFoundError:
        logging.error(f'GET /{app_name} {status.HTTP_404_NOT_FOUND} NOT FOUND')
        response.status_code = status.HTTP_404_NOT_FOUND
        return None

    except ExtraHTTPError:
        logging.error(
            f'GET /{app_name} {status.HTTP_429_TOO_MANY_REQUESTS} TOO MANY REQUESTS')
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return None

    else:
        return resp
