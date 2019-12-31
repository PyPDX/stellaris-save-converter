FROM python:3.6

WORKDIR /tmp/install
RUN pip install -U pip setuptools
COPY ./converter/requirements-top.txt ./converter/
COPY ./upload/requirements-top.txt ./upload/
COPY ./requirements-top.txt ./
RUN pip install -r requirements-top.txt

WORKDIR /src
COPY . .
