#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Must specify enviornment, beta or prod"
    exit 0
fi

ENV=$1
echo "env $ENV"

docker build -t wearebeautiful.info:$ENV .
