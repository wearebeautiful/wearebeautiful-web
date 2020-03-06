#!/bin/bash

docker build -f Dockerfile.dev -t wab-web .

docker run -it \
    --rm --name wab-web \
    -p 80:5000 \
    -v `pwd`:/code/wearebeautiful.info \
    -v ~/wearebeautiful/wearebeautiful-models:/archive \
    wab-web
