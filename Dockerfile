FROM python:alpine

ENV TZ=Europe/Berlin
ENV UNBUFFERED=1

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone; \
    apk --no-cache update; \
    apk add --no-cache libmagic ffmpeg speex

RUN adduser -D myuser
USER myuser
WORKDIR /home/myuser

COPY --chown=myuser:myuser app/ ./

ENV PATH="/home/myuser/.local/bin:${PATH}"

RUN pip install pip -U --no-cache-dir; \
    pip install --user --no-cache-dir -r requirements.txt 

ENTRYPOINT /bin/sh -c "export UNBUFFERED=1 && python3 -u fritzab2.py"
