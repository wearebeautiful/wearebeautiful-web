#!/bin/bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

docker run -d \
    --expose 3031 \
    --name wearebeautiful-web \
    -v /home/website/wearebeautiful-models:/models \
    -v $SRC_DIR/admin/nginx/vhost.d:/etc/nginx/vhost.d:ro \
    --env "VIRTUAL_HOST=wearebeautiful.info" \
    --env "LETSENCRYPT_HOST=wearebeautiful.info" \
    --env "LETSENCRYPT_EMAIL=mayhem@gmail.com" \
    --network=website-network \
    wearebeautiful.info:beta
