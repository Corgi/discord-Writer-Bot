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
        answers = [
            lib.get_string('8ball:0', guild_id),
            lib.get_string('8ball:1', guild_id),
            lib.get_string('8ball:2', guild_id),
            lib.get_string('8ball:3', guild_id),
            lib.get_string('8ball:4', guild_id),
            lib.get_string('8ball:5', guild_id),
            lib.get_string('8ball:6', guild_id),
            lib.get_string('8ball:7', guild_id),
            lib.get_string('8ball:8', guild_id),
            lib.get_string('8ball:0', guild_id),
            lib.get_string('8ball:10', guild_id),
            lib.get_string('8ball:11', guild_id),
            lib.get_string('8ball:12', guild_id),
            lib.get_string('8ball:13', guild_id),
            lib.get_string('8ball:14', guild_id),
            lib.get_string('8ball:15', guild_id),
            lib.get_string('8ball:16', guild_id),
            lib.get_string('8ball:17', guild_id),
            lib.get_string('8ball:18', guild_id),
            lib.get_string('8ball:19', guild_id),
            lib.get_string('8ball:20', guild_id)
        ]

        # Pick a random answer
        answer = random.choice(answers)

        # Send the message
        await context.send( '"' + format(question) + '"\n\n' + format(answer) )



def setup(bot):
    bot.add_cog(EightBall(bot))