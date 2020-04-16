FROM ubuntu:16.04

FROM alpine:3.8

COPY --from=0 /etc/apt/sources.list /etc/apt/sources.list

RUN apk add --no-cache curl jq && \
    export COUNTRY=$(curl ipinfo.io | jq '.country' | tr -d '"') && \
    sed -i "s|http:\/\/archive|http:\/\/$COUNTRY.archive|g" /etc/apt/sources.list
#"

FROM jupyterhub/jupyterhub:1.0.0

COPY --from=1 /etc/apt/sources.list /etc/apt/sources.list

RUN pip install notebook==6.0.1
RUN pip install oauthenticator==0.9.0
RUN pip install nbgrader

COPY ./main.min.js /opt/conda/lib/python3.6/site-packages/notebook/static/notebook/js

RUN apt-get update
RUN apt-get upgrade
