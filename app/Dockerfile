FROM python:3.9.5-slim

WORKDIR /app
COPY . /app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN pip install --no-cache-dir -r /app/requirements.txt
