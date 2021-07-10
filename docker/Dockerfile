# syntax=docker/dockerfile:1

FROM alpine:latest 

ENV TZ=Europe/Berlin
ENV UNBUFFERED=1

WORKDIR /app
VOLUME /app

COPY . .

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone; \
    /bin/sh -c 'apk update && apk add --no-cache gcc musl-dev python3-dev py3-wheel py3-pip py3-olm libffi-dev openssl-dev cargo zlib-dev jpeg-dev libmagic speex ffmpeg htop; \
    pip install update pip && pip install -r requirements.txt ; \
    apk del zlib-dev jpeg-dev gcc musl-dev python3-dev openssl-dev cargo;'



ENTRYPOINT ["python3", "-u", "fritzab2matrix.py "]
