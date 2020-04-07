#!/bin/bash

git pull origin master
./build.sh
./stop-containers.sh
./start-containers.sh
