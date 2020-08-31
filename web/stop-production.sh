#!/bin/bash

echo "---- stop wearebeautiful-logs"
docker stop wab-logs
docker rm wab-logs

echo "---- stop telegraf"
docker stop telegraf
docker rm telegraf

echo "---- stop wearebeautiful-web"
./stop-containers.sh

echo "---- stop proxy, le"
docker stop nginx le 
docker rm nginx le 

echo "---- done"
