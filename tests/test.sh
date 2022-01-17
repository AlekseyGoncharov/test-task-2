#!/usr/bin/env bash

docker-compose up -d --build
python test.py
docker-compose down