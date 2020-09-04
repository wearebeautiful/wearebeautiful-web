#!/bin/bash

sudo apt-get install -y influxdb

# Allow vulva & penis to connect to port 8086
sudo ufw allow from 95.216.117.155 to any port 8086
sudo ufw allow from 135.181.86.222 to any port 8086


echo "Setup complete!"
