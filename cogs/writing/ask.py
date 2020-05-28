import random
import lib
import discord
from discord.ext import commands
from structures.user import User
from structures.wrapper import CommandWrapper

class Ask(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self._arguments = [
            {
                'key': 'type',
                'prompt': 'ask:arguments',
                'required': True,
            }
        ]

    @commands.command(name="ask")
    async def ask(self, context, type=None):
        """
        Asks you a random question about your character or your world, to get the creative juices flowing.
        Initial questions taken from (novel-software).

        Examples:
            !ask c(haracter) - Asks you a question about your character
            !ask w(orld) - Asks you a question about your world
        """

        user = User(context.message.author.id, context.guild.id, context)

        # Check the arguments were all supplied and get a dict list of them and their values, after any prompts
        args = await self.check_arguments(context, type=type)
        if not args:
            return

        # Overwrite the variables passed in, with the values from the prompt and convert to lowercase
        type = args['type'].lower()

        if type in ('c', 'char', 'character'):
            options = lib.get_asset('q_char', user.get_guild())
        elif type in ('w', 'world'):
            options = lib.get_asset('q_world', user.get_guild())
        else:
            await context.send( user.get_mention() + ', ' + lib.get_string('ask:error', user.get_guild()) )
            return

        max = len(options) - 1
        rand = random.randint(1, max)
        question = options[rand]
        await context.send(f'[{rand}] {question}')

def setup(bot):
    bot.add_cog(Ask(bot))