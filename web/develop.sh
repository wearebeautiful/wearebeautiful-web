#!/bin/bash

docker build -f Dockerfile.dev -t wab-web .

docker run -it \
    --rm --name wab-web \
    -p 80:5000 \
    -v `pwd`:/code/wearebeautiful.info \
    -v `pwd`/../../wearebeautiful-models:/wearebeautiful-models \
    wab-web
