#!/bin/bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LOGDIR=/home/wab/logs
LOGDIR_UID=101
MODELS=/home/wab/wearebeautiful-models
DOMAIN=wearebeautiful.info

echo "---- start wearebeautiful web"
docker run -d \
    --expose 3031 \
    --name wab-web \
    --network=wab-network \
    -v $MODELS:/wearebeautiful-models \
    -v $SRC_DIR/admin/uwsgi/uwsgi.ini:/code/uwsgi.ini:ro \
    -v $SRC_DIR/admin/sockets:/sockets:rw \
    wearebeautiful.info:prod uwsgi --ini /code/uwsgi.ini

echo "---- create cache volume"
docker volume create --driver local --name wab-cache-volume

echo "---- start wearebeautiful comp"
mkdir -p $LOGDIR && sudo chown $LOGDIR_UID:$LOGDIR_UID $LOGDIR
docker run -d \
    --expose 8080 \
    --name wab-comp \
    -v wab-cache-volume:/cache \
    -v $MODELS:/models:ro \
    -v $SRC_DIR/admin/nginx/wab-comp.conf:/etc/nginx/nginx.conf:rw \
    -v $LOGDIR:/var/log/nginx:rw \
    -v $SRC_DIR/admin/sockets:/sockets:rw \
    --network=wab-network \
    --env "LETSENCRYPT_HOST=$DOMAIN" \
    --env "LETSENCRYPT_EMAIL=rob@wearebeautiful.info" \
    --env "VIRTUAL_HOST=$DOMAIN" \
    wearebeautiful.info:prod
