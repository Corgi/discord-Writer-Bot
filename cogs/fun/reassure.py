import random, lib, discord, json
from discord.ext import commands

# debugging
from pprint import pprint
from inspect import getmembers

class Reassure(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reassure")
    async def reassure(self, context, who=None):
        """
        Reassures you that everything will be okay.

        Examples: !reassure
        """

        guild_id = context.guild.id

        # If no name passed through, default to the author of the command
        if who is None:
            who = context.message.author.name

        user = context.guild.get_member_named(who)

        # If we couldn't find the user, display an error
        if user is None:
            await context.send( lib.get_string('err:nouser', guild_id) )
            return

        # Load the JSON file with the quotes
        quotes = lib.get_asset('reassure', guild_id)

        max = len(quotes) - 1
        quote = quotes[random.randint(1, max)]

        # Send the message
        await context.send( user.mention + ', ' + format(quote) )

def setup(bot):
    bot.add_cog(Reassure(bot))