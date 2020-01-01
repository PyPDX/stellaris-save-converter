FROM python:3.6

WORKDIR /tmp/install
RUN pip install -U pip setuptools
COPY ./converter/requirements-top.txt ./converter/
COPY ./presign/requirements-top.txt ./presign/
COPY ./requirements-top.txt ./
RUN pip install -r requirements-top.txt

WORKDIR /src
COPY . .
