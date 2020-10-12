#!/bin/bash

# Go backwards into the main directory.
cd ./../

# Make sure the file permissions haven't changed after git push.
chmod +x run.py

# Start it and redirect output.
nohup python3.8 -u run.py > logs/bot.log 2> logs/error.log < /dev/null &