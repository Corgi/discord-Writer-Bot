import random, lib, discord, json
from discord.ext import commands
from pprint import pprint

class Quote(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quote")
    async def quote(self, context):
        """
        A random motivational quote to inspire you.

        Examples: !quote
        """

        guild_id = context.guild.id

        # Load the JSON file with the quotes
        quotes = lib.get_asset('quotes', guild_id)

        max = len(quotes) - 1
        quote = quotes[random.randint(1, max)]

        # Send the message
        await context.send( format(quote.quote + ' - *' + quote.name + '*') )

def setup(bot):
    bot.add_cog(Quote(bot))