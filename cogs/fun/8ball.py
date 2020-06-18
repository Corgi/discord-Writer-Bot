import random
import lib
import discord
from discord.ext import commands
from structures.wrapper import CommandWrapper

class EightBall(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self._arguments = [
            {
                'key': 'question',
                'prompt': '8ball:arguments',
                'required': True
            }
        ]

    @commands.command(name="8ball")
    @commands.guild_only()
    async def _8ball(self, context, question=None):
        """
        Ask the magic 8-ball a question. Your question will be routed to a text-processing AI in order to properly analyze the content of the question and provide a meaningful answer.

        Examples: !8ball Should I do some writing?
        """

        guild_id = context.guild.id

        # Check the arguments were all supplied and get a dict list of them and their values, after any prompts
        args = await self.check_arguments(context, question=question)
        if not args:
            return

        # Overwrite variable from check_arguments()
        question = args['question']

        # Create array of possible answers to choose from
        answers = []

        # Load all 21 possible answers into an array to pick from
        for i in range(21):
            answers.append( lib.get_string('8ball:'+format(i), guild_id) )

        # Pick a random answer
        answer = random.choice(answers)

        # Send the message
        await context.send( context.message.author.mention + ', ' + format(answer) )

    # @_8ball.error
    # async def _8ball_error(self, context, error):
    #     """
    #
    #     :param context:
    #     :param error:
    #     :return:
    #     """
    #     if not isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
    #         print(error)

def setup(bot):
    bot.add_cog(EightBall(bot))