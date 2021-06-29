# syntax=docker/dockerfile:1

FROM ubuntu:latest

ENV TZ=Europe/Berlin

WORKDIR /app
VOLUME /app

COPY . .

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone; \
    /bin/bash -c 'apt update && apt install -y libolm-dev python3-pip ffmpeg htop; \
    pip install update pip && pip install -r requirements.txt ;'



ENTRYPOINT ["./fritzab2matrix.py "]














