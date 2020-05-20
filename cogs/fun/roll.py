import random
import lib
import discord
from discord.ext import commands

class Roll(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, context, roll='1d6'):
        """
        Rolls a dice between 1-6, or 1 and a specified number (max 100). Can also roll multiple dice at once (max 100) and get the total.
        Examples:
            !roll - Rolls one 6-sided die.
            !roll 8 - Rolls one 8-sided die.
            !roll 3d20 - Rolls three 20-sided dice.
            !roll 100d100 - Rolls the maximum, one-hundred 100-sided dice.
        """

        guild_id = context.guild.id

        # Make sure the format is correct (1d6)
        try:
            sides = int(roll.split('d')[1])
            rolls = int(roll.split('d')[0])
        except Exception as e:
            await context.send( lib.get_string('roll:format', guild_id) );
            return

        # Number of rolls or sides cannot be less than 1
        # Nor can they be more than 100
        if sides < 1:
            sides = 1
        elif sides > 100:
            sides = 100

        if rolls < 1:
            rolls = 1
        elif rolls > 100:
            rolls = 100

        total = 0
        output = ''

        # Roll the dice {rolls} amount of times
        for x in range(rolls):

            val = random.randint(1, sides)
            total += val
            output += ' [ '+str(val)+' ] '

        # Now print out the total
        output += '\n**'+lib.get_string('roll:total', guild_id) + str(total) + '**';

        await context.send( output )



def setup(bot):
    bot.add_cog(Roll(bot))