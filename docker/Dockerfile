# syntax=docker/dockerfile:1

FROM python:alpine

ENV TZ=Europe/Berlin
ENV UNBUFFERED=1

WORKDIR /app
VOLUME /app

COPY . .

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone; \
    apk --no-cache update && apk add --no-cache  --virtual .build-deps \
    gcc \
    cargo \
    libffi-dev \
    openssl-dev \
    olm-dev \
    zlib-dev \
    jpeg-dev ; \
    apk add --no-cache olm libmagic ffmpeg speex; \
    pip --no-cache-dir install upgrade pip; \
    pip install --no-cache-dir -r requirements.txt ; \
    apk del --no-cache .build-deps;



ENTRYPOINT ["python3", "-u", "fritzab2matrix.py "]
