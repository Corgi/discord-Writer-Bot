import discord, lib, pytz
from datetime import datetime, timezone
from discord.ext import commands
from structures.user import User
from structures.wrapper import CommandWrapper

class MySetting(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self._supported_settings = ['timezone']
        self._arguments = [
            {
                'key': 'setting',
                'prompt': 'mysetting:argument:setting',
                'required': True,
                'check': lambda content : content in self._supported_settings,
                'error': 'err:invalidsetting'
            },
            {
                'key': 'value',
                'prompt': 'mysetting:argument:value',
                'required': True
            }
        ]

    @commands.command(name="mysetting", aliases=['myset'])
    @commands.guild_only()
    async def my_setting(self, context, setting=None, value=None):
        """
        Lets you update a setting for your user account.

        **Note:** For the timezone setting, make sure the value you specify is a valid TZ Database Name from this wikipedia page:
        https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

        Examples:
            !mysetting timezone Europe/London
            !mysetting timezone America/Phoenix
        """
        user = User(context.message.author.id, context.guild.id, context)

        # If we want to list the setting, do that instead.
        if setting is not None and setting.lower() == 'list':
            settings = user.get_settings()
            output = '```ini\n';
            if settings:
                for setting, value in settings.items():
                    output += setting + '=' + str(value) + '\n'
            else:
                output += lib.get_string('setting:none', guild.get_id())
            output += '```'
            return await context.send(user.get_mention() + ',\n' + output)

        # Check the arguments are valid
        args = await self.check_arguments(context, setting=setting, value=value)
        if not args:
            return

        setting = args['setting'].lower()
        value = args['value']

        # If the setting is timezone convert the value
        if setting == 'timezone':
            try:
                timezone = pytz.timezone(value)
                time = datetime.now(timezone)
                offset = datetime.now(timezone).strftime('%z')
                await context.send( lib.get_string('event:timezoneupdated', user.get_guild()).format(value, time.ctime(), offset) )
            except pytz.exceptions.UnknownTimeZoneError:
                await context.send(lib.get_string('mysetting:timezone:help', user.get_guild()))
                return

        # Update the setting and post the success message
        user.update_setting(setting, value)
        await context.send( user.get_mention() + ', ' + lib.get_string('mysetting:updated', user.get_guild()).format(setting, value) )

def setup(bot):
    bot.add_cog(MySetting(bot))