import discord, lib
from discord.ext import commands
from structures.db import Database
from structures.user import User
from structures.wrapper import CommandWrapper

class Goal(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self.__db = Database.instance()
        self._arguments = [
            {
                'key': 'option',
                'prompt': 'goal:argument:option',
                'required': True
            },
            {
                'key': 'value',
                'required': False
            }
        ]

    @commands.command(name="goal")
    @commands.guild_only()
    async def goal(self, context, option=None, value=None):
        """
        Sets a daily goal which resets every 24 hours at midnight in your timezone.

        Examples:
            !goal - Checks how close you are to your daily goal
            !goal set 500 - Sets your daily goal to be 500 words per day
            !goal cancel - Deletes your daily goal
        """

        if option == 'set':
            return await self.run_set(context, value)
        elif option == 'cancel' or option == 'delete' or option == 'reset':
            return await self.run_cancel(context)
        else:
            return await self.run_check(context)

    async def run_cancel(self, context):

        user = User(context.message.author.id, context.guild.id, context)

        # Currently only daily goals implemented
        type = 'daily'

        user.delete_goal(type)
        return await context.send(user.get_mention() + ', ' + lib.get_string('goal:givenup', user.get_guild()))

    async def run_set(self, context, amount):

        user = User(context.message.author.id, context.guild.id, context)

        # Currently only daily goals implemented
        type = 'daily'

        # Check if we can convert the amount to an int
        amount = lib.is_number(amount)
        if not amount:
            return await context.send(user.get_mention() + ', ' + lib.get_string('err:validamount', user.get_guild()))

        # Set the user's goal
        user.set_goal(type, amount)
        timezone = user.get_setting('timezone') or 'UTC'

        return await context.send(user.get_mention() + ', ' + lib.get_string('goal:set', user.get_guild()).format(type, amount, timezone))

    async def run_check(self, context):

        user = User(context.message.author.id, context.guild.id, context)

        # Currently only daily goals implemented
        type = 'daily'

        user_goal = user.get_goal(type)
        if user_goal:
            progress = user.get_goal_progress(type)
            return await context.send(user.get_mention() + ', ' + lib.get_string('goal:status', user.get_guild()).format(progress['str'], progress['percent'], type, progress['current'], progress['goal']))
        else:
            return await context.send(user.get_mention() + ', ' + lib.get_string('goal:nogoal', user.get_guild()).format(type))


def setup(bot):
    bot.add_cog(Goal(bot))