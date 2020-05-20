import random
import lib
import discord
from discord.ext import commands

class EightBall(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball")
    async def _8ball(self, context, question):
        """
        Ask the magic 8-ball a question. Your question will be routed to a text-processing AI in order to properly analyze the content of the question and provide a meaningful answer.

        Examples: !8ball Should I do some writing?
        """

        guild_id = context.guild.id

        # Create array of possible answers to choose from
        answers = []

        # Load all 21 possible answers into an array to pick from
        for i in range(21):
            answers.append( lib.get_string('8ball:'+format(i), guild_id) )

        # Pick a random answer
        answer = random.choice(answers)

        # Send the message
        await context.send( context.message.author.mention + '\n' + format(answer) )

def setup(bot):
    bot.add_cog(EightBall(bot))