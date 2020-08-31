#!/bin/bash

# only log ufw stuff to one file (/var/log/ufw.log by default)
sed -i 's/^#& stop/\& stop/' /etc/rsyslog.d/20-ufw.conf && systemctl restart rsyslog

ufw route allow proto tcp from any to any port 443
ufw allow from 135.181.45.162 to any port 8086
ufw allow from 95.217.160.238 to any port 8086

ufw enable
ufw status verbose
