import json
import logging
import os
from contextlib import contextmanager
from io import BytesIO
from tokenize import tokenize
from zipfile import ZipFile

import boto3
from clausewitz.parse import parse
from clausewitz.util.tokenize import prepare

ENCODING = 'utf-8'
s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']
EXPIRATION = int(os.environ.get('EXPIRATION', 60))  # default: 1 min

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@contextmanager
def get_s3_file(key) -> BytesIO:
    logger.info(f"Downloading '{key}' to memory")
    with BytesIO() as f:
        s3.download_fileobj(BUCKET_NAME, key, f)
        f.seek(0)
        yield f


def unzip_save(f: BytesIO):
    with ZipFile(f) as zip:
        with zip.open('meta') as meta:
            logger.info('Parsing meta')
            yield 'meta', meta
        # TODO this takes too long..
        # with zip.open('gamestate') as gamestate:
        #     logger.info('Parsing gamestate')
        #     yield 'gamestate', gamestate


def jsonify(f):
    return parse(tokenize(prepare(f.readline)))


def upload(key, data):
    binary_data = json.dumps(
        data,
        separators=(',', ':'),
    ).encode(ENCODING)
    logger.info(f"Uploading {len(binary_data)} bytes to '{key}'")

    with BytesIO(binary_data) as f:
        s3.upload_fileobj(f, BUCKET_NAME, key)


def presign_download(key):
    return s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': key,
        },
        ExpiresIn=EXPIRATION,
    )


def lambda_handler(event, context):
    data = json.loads(event['body'])

    key = data['key']
    with get_s3_file(key) as f:
        result = {
            name: jsonify(unzipped)
            for name, unzipped in unzip_save(f)
        }

    try:
        save_name = result['meta']['name'].strip('"') + ' - ' + result['meta']['date'].strip('"')
    except KeyError:
        save_name = 'converted'

    new_key = f"{os.path.dirname(key)}/{save_name}.json"
    upload(new_key, result)
    download_url = presign_download(new_key)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST',
        },
        'body': json.dumps({
            'url': download_url,
        }),
    }
