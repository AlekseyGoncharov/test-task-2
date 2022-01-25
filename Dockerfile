FROM python:3.9-alpine

ADD /app /app
WORKDIR /app
RUN apk update && apk add --no-cache postgresql-dev gcc python3-dev musl-dev
RUN pip install -r requirements.txt
RUN apk del gcc
RUN addgroup -g 2000 python-app \
    && adduser -u 2000 -G python-app -s /bin/sh -D python-app

USER 2000

CMD gunicorn --bind 0.0.0.0:5000 wsgi:app