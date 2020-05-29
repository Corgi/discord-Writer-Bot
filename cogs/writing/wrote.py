import discord, lib
from discord.ext import commands
from structures.db import Database
from structures.user import User
from structures.wrapper import CommandWrapper

class Wrote(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self.__db = Database.instance()
        self._arguments = [
            {
                'key': 'amount',
                'prompt': 'wrote:argument:amount',
                'required': True,
                'type': int,
                'error': 'wrote:err:type'
            },
            {
                'key': 'shortname',
                'required': False
            }
        ]

    @commands.command(name="wrote")
    async def wrote(self, context, amount=None, shortname=None):
        """
        Adds to your total words written statistic.

        Examples:
            !wrote 250 - Adds 250 words to your total words written
            !wrote 200 sword - Adds 200 words to your Project with the shortname "sword". (See: Projects for more info).
        """

        user = User(context.message.author.id, context.guild.id, context)

        # Check the arguments are valid
        args = await self.check_arguments(context, amount=amount, shortname=shortname)
        if not args:
            return

        amount = args['amount']
        shortname = args['shortname'].lower() if shortname is not None else None

        # # Did they specify a Project shortname?
        # # TODO
        #
        # # Is there an Event running?
        # # TODO
        #
        # # Increment their words written statistic
        user.add_stat('total_words_written', amount)

        # # Update their words towards their daily goal
        # # TODO
        #
        # Output message
        total = user.get_stat('total_words_written')
        return await context.send( user.get_mention() + ', ' + lib.get_string('wrote:added', user.get_guild()).format(str(amount), str(total)) )


def setup(bot):
    bot.add_cog(Wrote(bot))