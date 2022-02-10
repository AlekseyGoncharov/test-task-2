FROM python:3.9-alpine
MAINTAINER "SnakeDex"

add . /app
WORKDIR /app

RUN apk update && apk add postgresql-dev gcc musl && apk cleancache
RUN pip install -r requirements.txt
RUN apk del gcc
EXPOSE 8080

CMD ["python", "app.py"]