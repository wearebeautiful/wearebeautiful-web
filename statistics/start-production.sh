#!/bin/bash

HOSTNAME=`hostname`

echo "---- create network"
docker network create wab-network

echo "---- create grafana volume"
docker volume create --driver local --name grafana-volume

echo "---- start telegraf"
sed 's/%hostname%/'$HOSTNAME'/g' telegraf.conf.in > telegraf.conf
docker run -d \
    --name telegraf \
    --network=host \
    -e HOST_PROC=/host/proc \
    -v /proc:/host/proc:ro \
    -v `pwd`/telegraf.conf:/etc/telegraf/telegraf.conf:ro \
    --restart unless-stopped \
    telegraf:1.13.4

echo "---- start grafana"
docker run -d \
    -p "3000:3000" \
    --name grafana \
    --network=host \
    --restart unless-stopped \
    -v grafana-volume:/var/lib/grafana \
    grafana/grafana:7.1.5

sudo ufw-docker allow grafana 3000
