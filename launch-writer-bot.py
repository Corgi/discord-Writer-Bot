#!/usr/bin/env python3

from pprint import pprint

import json
import discord
import lib
from bot import WriterBot
from discord.ext import commands

# Load the settings for intial setup
config = lib.get('./settings.json')

# Load the Bot object
bot = WriterBot(command_prefix=config.prefix)

# Load all commands
bot.load_commands()

# Start the bot
bot.run(config.token)