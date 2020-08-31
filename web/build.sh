#!/bin/bash


echo "---- wearebeautiful-logs"
cd ../logging
./build.sh
cd -

echo "---- wearebeautiful-web"
docker build -t wearebeautiful.info:prod .

echo "---- DONE"
