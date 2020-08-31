#!/bin/bash

echo "---- stop wearebeautiful-logs"
docker stop wab-logs
docker rm wab-logs

echo "---- stop wearebeautiful-web"
cd ../wearebeautiful-web
./stop-containers.sh
cd -

echo "---- stop proxy, le"
docker stop nginx le 
docker rm nginx le 

echo "---- done"
