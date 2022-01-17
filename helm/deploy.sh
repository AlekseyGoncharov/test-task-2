#!/usr/bin/env bash

docker build -t test-app:test ../.
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.1.0/deploy/static/provider/cloud/deploy.yaml
kubectl create ns test-app
kubectl config set-context --current --namespace=test-app
helm dependency update postgresql
helm install test-app-postgre postgresql
helm install test-app app