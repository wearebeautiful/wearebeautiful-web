#!/bin/bash

echo "---- create network"
docker network create wab-network

echo "---- create influx volume"
docker volume create --driver local --name influx-volume
echo "---- create grafana volume"
docker volume create --driver local --name grafana-volume

echo "---- start influxdb"
docker run -d \
    -p "8086:8086" \
    --name influxdb \
    --restart unless-stopped \
    --network=wab-network \
    -v influx-volume:/var/lib/influxdb \
    influxdb:1.7.10

echo "---- start telegraf"
sed 's/%hostname%/penis/g' telegraf.conf.in > telegraf.conf
docker run -d \
    --name telegraf \
    --network=wab-network \
    -e HOST_PROC=/host/proc \
    -v /proc:/host/proc:ro \
    -v `pwd`/telegraf.conf:/etc/telegraf/telegraf.conf:ro \
    --restart unless-stopped \
    telegraf:1.13.4

echo "---- start grafana"
docker run -d \
    -p "3000:3000" \
    --name grafana \
    --network=wab-network \
    --restart unless-stopped \
    -v grafana-volume:/var/lib/grafana \
    grafana/grafana:7.1.5
ufw-docker allow grafana 3000
