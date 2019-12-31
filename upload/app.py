import json
import os
import uuid
from datetime import datetime

import boto3

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']
EXPIRATION = int(os.environ.get('EXPIRATION', 60))  # default: 1 min


def presign_upload(key):
    return s3.generate_presigned_post(
        BUCKET_NAME,
        key,
        ExpiresIn=EXPIRATION,
    )


def lambda_handler(event, context):
    now = datetime.now()
    key = f'{now.year}/{now.month}/{now.day}/{uuid.uuid4()}/save.zip'

    response = presign_upload(key)

    return {
        'statusCode': 200,
        'body': json.dumps(response),
    }
