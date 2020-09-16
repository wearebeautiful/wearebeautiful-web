#!/bin/bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
HOSTNAME=`hostname`
WAB_DOMAIN=`echo "import config; print(config.SITE_DOMAIN)" | python3`

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

sudo ufw-docker delete allow wab-logs 8000
sudo ufw-docker delete allow wab-logs 8001

echo "---- start telegraf"
docker run -d \
    -p "9273:9273" \
    --name telegraf \
    --network=wab-network \
    --hostname=`hostname` \
    -e HOST_PROC=/host/proc \
    -v /proc:/host/proc:ro \
    -v `pwd`/telegraf.conf:/etc/telegraf/telegraf.conf:ro \
    -v /home/wab/logs:/logs:ro \
    --restart unless-stopped \
    telegraf:1.15.2

# docker exec -it telegraf telegraf --config /etc/telegraf/telegraf.conf --test


echo "---- enable firewall ports for services"
sudo ufw-docker allow nginx 443
sudo ufw-docker allow nginx 80

echo "---- clear cache"
docker exec -it wab-comp admin/clear_cache.sh

echo "---- done"
