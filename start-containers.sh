#!/bin/bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LOGDIR=/tmp/
MODELS=/home/wab/wearebeautiful-models
DOMAIN=test.wearebeautiful.info

docker run -d \
    --expose 3031 \
    --name wab-web \
    --network=wab-network \
    -v $MODELS:/archive \
    wearebeautiful.info:prod

#    --env "VIRTUAL_HOST=wab-dev" \

docker run -d \
    --expose 8080 \
    --name wab-comp \
    -v wab-cache:/cache \
    -v $MODELS:/models:ro \
    -v $SRC_DIR/admin/nginx/cache/cache.conf:/etc/nginx/conf.d/cache.conf:ro \
    -v $SRC_DIR/admin/nginx/vhost.d/wearebeautiful.info:/etc/nginx/vhost.d/$DOMAIN:ro \
    -v $SRC_DIR/admin/nginx/compressor/compressor-nginx.conf:/etc/nginx/nginx.conf:rw \
    -v $LOGDIR:/var/log/nginx:rw \
    --network=wab-network \
    --env "LETSENCRYPT_HOST=$DOMAIN" \
    --env "LETSENCRYPT_EMAIL=rob@wearebeautiful.info" \
    --env "VIRTUAL_HOST=$DOMAIN" \
    nginx:1.17.8


