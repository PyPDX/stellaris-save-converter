FROM python:3.6

WORKDIR /tmp/install
RUN pip install -U pip setuptools
COPY ./hello_world/requirements-top.txt ./hello_world/
COPY ./requirements-top.txt ./
RUN pip install -r requirements-top.txt

WORKDIR /src
COPY . .
