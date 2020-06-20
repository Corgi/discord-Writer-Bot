import discord
from discord.ext import commands

class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    @commands.guild_only()
    async def ping(self, context):
        """
        Displays latency between client and bot
        """
        latency = round(self.bot.latency * 1000, 2)
        return await context.send('Pong! ' + str(latency) + 'ms')


def setup(bot):
    bot.add_cog(Ping(bot))