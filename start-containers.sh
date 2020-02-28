#!/bin/bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

docker run -d \
    --expose 3031 \
    --name wab-web \
    --network=website-network \
    -v wab-models:/archive \
    wearebeautiful.info:prod

#    --env "VIRTUAL_HOST=wab-dev" \
docker run -d \
    --expose 8080 \
    --name wab-comp \
    -v wab-cache:/cache \
    -v $SRC_DIR/admin/nginx/cache/cache.conf:/etc/nginx/conf.d/cache.conf:ro \
    -v $SRC_DIR/admin/nginx/compressor/compressor-nginx.conf:/etc/nginx/nginx.conf:ro \
    --network=website-network \
    --env "LETSENCRYPT_HOST=wearebeautiful.info" \
    --env "LETSENCRYPT_EMAIL=mayhem@gmail.com" \
    --env "VIRTUAL_HOST=wearebeautiful.info" \
    nginx:1.17.8


