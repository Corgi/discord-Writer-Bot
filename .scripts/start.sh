#!/usr/bin/env bash

# Make sure the file permissions haven't changed after git push.
chmod +x /var/www/discord-Writer-Bot/bot.py

# Start it and redirect output.
nohup python3 -u /var/www/discord-Writer-Bot/bot.py > /var/www/discord-Writer-Bot/logs/out.log &