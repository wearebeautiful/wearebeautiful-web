#!/bin/bash

echo "---- wearebeautiful-logs"
cd logging
./build.sh
cd -

echo "---- wearebeautiful-web"

cd ../wearebeautiful-web
./build.sh
cd -

echo "---- DONE"
