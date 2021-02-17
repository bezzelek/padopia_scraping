FROM python:3.8.3-alpine3.12

ENV PYTHONPATH="$PYTHONPATH:/app/src" \
    FLASK_ENV="development"

COPY ["requirements.txt", "/app/"]


RUN apk add --update --no-cache make bash libpq
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apk add --update --no-cache g++ gcc libxslt-dev
RUN apk add --no-cache zlib-dev jpeg-dev
RUN apk add --no-cache --virtual build \
    build-base \
    musl-dev \
    libffi-dev \
    openssl-dev \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir pymongo[srv] \
    && pip install --no-cache-dir pymongo[tls] \
    && apk del build

WORKDIR /app
EXPOSE 5000
