import discord, lib
from discord.ext import commands
from structures.guild import Guild
from structures.user import User
from structures.wrapper import CommandWrapper

class Reset(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self._supported_resets = ['pb', 'wc', 'xp', 'projects', 'all']
        self._arguments = [
            {
                'key': 'what',
                'prompt': 'reset:argument:what',
                'required': True,
                'check': lambda content: content in self._supported_resets,
                'error': 'reset:invalid'
            },
            {
                'key': 'confirm',
                'prompt': 'reset:argument:confirm',
                'required': True,
                'check': lambda content : content in ('y', 'yes', 'n', 'no')
            }
        ]

    @commands.command(name="reset")
    @commands.guild_only()
    async def reset(self, context, what=None, confirm=None):
        """
        Lets you reset your statistics/records.

        Examples:
            !reset pb: Resets your wpm personal best
            !reset wc: Resets your total word count
            !reset xp: Resets your xp/level to 0
            !reset all: Resets your xp/levels, stats, records, goals and challenges
        """

        user = User(context.message.author.id, context.guild.id, context)

        # Check the arguments are valid
        args = await self.check_arguments(context, what=what, confirm=confirm)
        if not args:
            return

        what = args['what'].lower()
        confirm = args['confirm'].lower()

        # Make sure they confirmed it, otherwise just stop and display an OK message
        if confirm not in ('y', 'yes'):
            output = 'OK'
            return await context.send(user.get_mention() + ', ' + output)

        # Personal Best
        if what == 'pb':
            user.update_record('wpm', 0)
            output = lib.get_string('reset:pb', user.get_guild())

        elif what == 'wc':
            user.update_stat('total_words_written', 0)
            output = lib.get_string('reset:wc', user.get_guild())

        elif what == 'xp':
            await user.update_xp(0)
            output = lib.get_string('reset:xp', user.get_guild())

        elif what == 'projects':
            user.reset_projects()
            output = lib.get_string('reset:projects', user.get_guild())

        elif what == 'all':
            user.reset()
            output = lib.get_string('reset:done', user.get_guild())

        return await context.send( user.get_mention() + ', ' + output )


def setup(bot):
    bot.add_cog(Reset(bot))