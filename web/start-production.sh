#!/bin/bash

WAB_DOMAIN=wearebeautiful.info
SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "---- start nginx proxy, le"

docker network create wab-network

docker run -d -p 80:80 -p 443:443 \
   --name nginx \
   -v /etc/ssl/le-certs:/etc/nginx/certs:ro \
   -v /etc/nginx/vhost.d \
   -v /usr/share/nginx/html \
   -v /var/run/docker.sock:/tmp/docker.sock:ro \
   -v `pwd`/nginx/vhost.d/wearebeautiful.info:/etc/nginx/vhost.d/$WAB_DOMAIN:ro \
   --label com.github.jrcs.letsencrypt_nginx_proxy_companion.nginx_proxy \
   --restart unless-stopped \
   --network=wab-network \
   jwilder/nginx-proxy

docker run -d \
   --name le \
   -v /var/run/docker.sock:/var/run/docker.sock:ro \
   -v /etc/ssl/le-certs:/etc/nginx/certs:rw \
   --volumes-from nginx \
   --restart unless-stopped \
   --network=wab-network \
   jrcs/letsencrypt-nginx-proxy-companion

echo "---- start wearebeautiful-web"
./start-containers.sh

echo "---- start wearebeautiful-logs"
docker run -d \
    --name wab-logs \
    -v /home/wab/logs:/var/log/nginx \
    -v /home/wab/goaccess:/goaccess \
    -v /home/wab/goaccess-html:/html \
    -p "8000:8000" \
    -p "8001:8001" \
    --restart unless-stopped \
    --network=wab-network \
    wearebeautiful-logs

echo "---- start telegraf"
sed 's/%hostname%/penis/g' telegraf.conf.in > telegraf.conf
docker run -d \
    --name telegraf \
    --network=wab-network \
    -e HOST_PROC=/host/proc \
    -v /proc:/host/proc:ro \
    -v `pwd`/telegraf.conf:/etc/telegraf/telegraf.conf:ro \
    --restart unless-stopped \
    telegraf:1.13.4


echo "---- enable firewall ports for services"
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

echo "---- done"
