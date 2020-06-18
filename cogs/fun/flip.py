import random
import lib
import discord
from discord.ext import commands

class Flip(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def flip(self, context):
        """
        Flips a coin
        Examples: !flip
        """

        guild_id = context.guild.id
        rand = random.randrange(2)
        side = 'heads' if rand == 0 else 'tails'

        await context.send( lib.get_string('flip:'+side, guild_id) )



def setup(bot):
    bot.add_cog(Flip(bot))