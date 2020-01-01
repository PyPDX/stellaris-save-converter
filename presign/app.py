import json
import os
import uuid
from datetime import datetime
from io import BytesIO

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']
EXPIRATION = int(os.environ.get('EXPIRATION', 60))  # default: 1 min


def presign_upload(key):
    return s3.generate_presigned_post(
        BUCKET_NAME,
        key,
        ExpiresIn=EXPIRATION,
    )


def upload_lambda_handler(event, context):
    now = datetime.now()
    key = f'{now.year}/{now.month}/{now.day}/{uuid.uuid4()}/save.zip'

    response = presign_upload(key)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET',
        },
        'body': json.dumps(response),
    }


def get_s3_file_content(key):
    with BytesIO() as f:
        try:
            s3.download_fileobj(BUCKET_NAME, key, f)
        except ClientError:
            return None
        f.seek(0)
        return f.read().decode()


def presign_download(key):
    return s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': key,
        },
        ExpiresIn=EXPIRATION,
    )


def check(key):
    dirname = os.path.dirname(key)
    err_msg = get_s3_file_content(f'{dirname}/ERROR')
    if err_msg is not None:
        return {
            'status': 'error',
        }

    success_msg = get_s3_file_content(f'{dirname}/SUCCESS')
    if success_msg is not None:
        return {
            'status': 'success',
            'url': presign_download(success_msg),
        }

    return {
        'status': 'processing',
    }


def download_lambda_handler(event, context):
    data = event['queryStringParameters']

    key = data['key']
    result = check(key)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET',
        },
        'body': json.dumps(result),
    }
