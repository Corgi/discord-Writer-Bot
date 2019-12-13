#!/usr/bin/env bash

cd /var/www/discord-Writer-Bot/

# Make sure the file permissions haven't changed after git push.
chmod +x launch-writer-bot.py

# Start it and redirect output.
nohup python3 -u launch-writer-bot.py > logs/out.log &