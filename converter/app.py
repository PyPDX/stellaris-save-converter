import json
import logging
import os
import traceback
from contextlib import contextmanager
from io import BytesIO
from pprint import pformat
from tokenize import tokenize
from zipfile import ZipFile

import boto3
from clausewitz.parse import parse
from clausewitz.util.tokenize import prepare

ENCODING = 'utf-8'
s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']

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
        with zip.open('gamestate') as gamestate:
            logger.info('Parsing gamestate')
            yield 'gamestate', gamestate


def jsonify(f):
    return parse(tokenize(prepare(f.readline)))


def upload(key, data, *, json_=True):
    if json_:
        s = json.dumps(
            data,
            separators=(',', ':'),
        )
    else:
        s = str(data)

    binary_data = s.encode(ENCODING)
    logger.info(f"Uploading {len(binary_data)} bytes to '{key}'")

    with BytesIO(binary_data) as f:
        s3.upload_fileobj(f, BUCKET_NAME, key)


def handle(key):
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
    return new_key


def lambda_handler(event, context):
    for record in event['Records']:
        logger.info(pformat(record))
        key = record['s3']['object']['key']
        if not key.endswith('/save.zip'):
            continue
        dirname = os.path.dirname(key)
        if not dirname:
            continue

        try:
            new_key = handle(key)
        except Exception:
            tb = traceback.format_exc()
            upload(f'{dirname}/ERROR', tb, json_=False)
            logger.error(tb)
        else:
            upload(f'{dirname}/SUCCESS', new_key, json_=False)
