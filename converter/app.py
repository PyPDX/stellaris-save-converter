import json
from io import BytesIO
from tokenize import tokenize
from zipfile import ZipFile

from clausewitz.parse import parse
from clausewitz.util.tokenize import prepare
from requests_toolbelt.multipart import decoder

ENCODING = 'utf-8'


def get_field_name(content_disposition: bytes):
    content_disposition = content_disposition.decode(ENCODING)
    for field in content_disposition.split(';'):
        field = field.strip()
        if not field.startswith('name='):
            continue
        return field[5:].strip('"')
    return None


def unzip_save(f: BytesIO):
    with ZipFile(f) as zip:
        with zip.open('meta') as meta:
            yield meta
        with zip.open('gamestate') as gamestate:
            yield gamestate


def jsonify(f):
    return parse(tokenize(prepare(f.readline)))


def lambda_handler(event, context):
    multipart_data = decoder.MultipartDecoder(
        event['body'].encode(ENCODING),
        event['headers']['Content-Type'],
        encoding=ENCODING,
    )

    meta = None
    gamestate = None
    for part in multipart_data.parts:
        name = get_field_name(part.headers[b'Content-Disposition'])
        with BytesIO(part.content) as f:
            if name == 'meta':
                meta = jsonify(f)
            elif name == 'gamestate':
                gamestate = jsonify(f)
            elif name == 'file':
                unzipped = unzip_save(f)
                meta = jsonify(next(unzipped))
                gamestate = jsonify(next(unzipped))

    return {
        "statusCode": 200,
        "body": json.dumps({
            'meta': meta,
            'gamestate': gamestate,
        }),
    }
