import discord, lib
from discord.ext import commands
from structures.db import Database
from structures.project import Project
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
    @commands.guild_only()
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
        shortname = args['shortname']
        message = None

        # If they were writing in a Project, update its word count.
        if shortname is not None:

            project = user.get_project(shortname.lower())

            # Make sure the project exists.
            if not project:
                return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:noexists', user.get_guild()).format(shortname))

            project.add_words(amount)
            message = lib.get_string('wrote:addedtoproject', user.get_guild()).format(str(amount), project.get_title())

        # # Is there an Event running?
        # # TODO

        # Increment their words written statistic
        user.add_stat('total_words_written', amount)

        # Update their words towards their daily goal
        await user.add_to_goal('daily', amount)

        # Output message
        if message is None:
            total = user.get_stat('total_words_written')
            message = lib.get_string('wrote:added', user.get_guild()).format(str(amount), str(total))

        await context.send(user.get_mention() + ', ' + message)


def setup(bot):
    bot.add_cog(Wrote(bot))