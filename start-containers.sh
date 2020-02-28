#!/bin/bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "$SRC_DIR"

#    --expose 3031 \
docker run -d \
    -p 3031:3031 \
    --name wab-web \
    --network=website-network \
    -v wab-models:/archive \
    wearebeautiful.info:prod

#    --env "LETSENCRYPT_HOST=wearebeautiful.info" \
#    --env "LETSENCRYPT_EMAIL=mayhem@gmail.com" \
#    --env "VIRTUAL_HOST=wearebeautiful.info" \
#    --expose 8080 \
docker run -d \
    -p 8080:80 \
    --name wab-comp \
    -v wab-cache:/cache \
    -v /Users/robert/wearebeautiful/wearebeautiful-web/admin/nginx/cache/cache.conf:/etc/nginx/conf.d/cache.conf:ro \
    -v $SRC_DIR/admin/nginx/compressor/compressor-nginx.conf:/etc/nginx/nginx.conf:ro \
    --env "VIRTUAL_HOST=wab-dev" \
    --network=website-network \
    nginx:1.17.8
