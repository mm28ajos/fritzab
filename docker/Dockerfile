# syntax=docker/dockerfile:1

FROM ubuntu:latest

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app
VOLUME /app

COPY . .

RUN ls -la
RUN ["cat", "/app/requirements.txt"]

RUN /bin/bash -c 'apt update && apt install -y libolm-dev python3-pip ffmpeg;'


RUN pip install update pip && pip install -r requirements.txt


CMD python3 fritzab2matrix.py && tail -f /dev/null













