import discord, lib
from discord.ext import commands
from structures.user import User
from structures.wrapper import CommandWrapper

class Reset(commands.Cog, CommandWrapper):



    def __init__(self, bot):
        self.bot = bot
        self._supported_resets = ['pb', 'wc', 'xp', 'all', 'server']
        self._arguments = [
            {
                'key': 'what',
                'prompt': 'reset:argument:what',
                'required': True
            },
            {
                'key': 'confirm',
                'prompt': 'reset:argument:confirm',
                'required': True,
                'check': lambda content : content in ('y', 'yes', 'n', 'no')
            }
        ]

    @commands.command(name="reset")
    async def reset(self, context, what=None, confirm=None):
        """
        Lets you reset your server statistics.

        Examples:
            !reset pb: Resets your wpm personal best on the server
            !reset wc: Resets your total word count on the server
            !reset xp: Resets your xp/level to 0
            !reset all: Resets all your stats which can be reset on the server
            !reset server: Resets the entire server stats, records and xp/levels (if you have mod permissions)
        """

        user = User(context.message.author.id, context.guild.id, context)

        # Check the arguments are valid
        args = await self.check_arguments(context, what=what, confirm=confirm)
        if not args:
            return

        what = args['what'].lower()
        confirm = args['confirm'].lower()

        # Make sure the reset option is one of the supported ones
        if what not in self._supported_resets:
            return await context.send( lib.get_string('reset:invalid', user.get_guild()).format( ','.join('`{}`'.format(el) for el in self._supported_resets ) ) )

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

        elif what == 'all':
            user.reset()
            output = lib.get_string('reset:done', user.get_guild())

        elif what == 'server':
            pass

        return await context.send( user.get_mention() + ', ' + output )


def setup(bot):
    bot.add_cog(Reset(bot))