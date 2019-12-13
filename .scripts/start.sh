#!/usr/bin/env bash

cd /var/www/discord-Writer-Bot/

# Make sure the file permissions haven't changed after git push.
chmod +x run.py

# Start it and redirect output.
nohup python3 -u run.py > logs/out.log &