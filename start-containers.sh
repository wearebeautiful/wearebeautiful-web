#!/bin/bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "$SRC_DIR"

#    -v /home/website/wearebeautiful-models:/models \
docker run -d \
    --expose 3031 \
    --name wab-web \
    --network=website-network \
    wearebeautiful.info:beta

#    --env "LETSENCRYPT_HOST=wearebeautiful.info" \
#    --env "LETSENCRYPT_EMAIL=mayhem@gmail.com" \
docker run -d \
    --expose 80 \
    --name wab-comp \
    -v $SRC_DIR/admin/nginx/compressor-nginx.conf:/etc/nginx/nginx.conf:ro \
    --env "VIRTUAL_HOST=wearebeautiful.info" \
    --network=website-network \
    nginx:1.17.8
