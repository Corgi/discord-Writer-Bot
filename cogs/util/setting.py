import discord, lib, pytz
from datetime import datetime, timezone
from discord.ext import commands
from structures.guild import Guild
from structures.user import User
from structures.wrapper import CommandWrapper

from pprint import pprint

class Setting(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self._supported_settings = ['lang', 'sprint_delay_end', 'prefix']
        self._arguments = [
            {
                'key': 'setting',
                'prompt': 'setting:argument:setting',
                'required': True,
                'check': lambda content: content in self._supported_settings,
                'error': 'err:invalidsetting'
            },
            {
                'key': 'value',
                'prompt': 'setting:argument:value',
                'required': True
            }
        ]

    @commands.command(name="setting")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def setting(self, context, setting=None, value=None):
        """
        Lets you update a setting for the server, if you have the permissions to manage_guild

        Examples:
            !setting lang en - Set the language to be used. Available language packs: en
            !setting sprint_delay_end 5 - Set the timer delay between the sprint finishing and the final word counts being tallied. Max time: 15 mins. Default: 2 mins.
            !setting list - Displays a list of all the custom server settings
        """
        user = User(context.message.author.id, context.guild.id, context)
        guild = Guild(context.guild)

        # If we want to list the setting, do that instead.
        if setting is not None and setting.lower() == 'list':
            settings = guild.get_settings()
            output = '```ini\n';
            if settings:
                for setting, value in settings.items():
                    output += setting + '=' + str(value) + '\n'
            else:
                output += lib.get_string('setting:none', guild.get_id())
            output += '```'
            return await context.send(output)

        # Otherwise, continue on as we must be trying to set a setting value
        # Check the arguments are valid
        args = await self.check_arguments(context, setting=setting, value=value)
        if not args:
            return

        setting = args['setting'].lower()
        value = args['value']

        guild.update_setting(setting, value)
        return await context.send(user.get_mention() + ', ' + lib.get_string('setting:updated', guild.get_id()).format(setting, value))

    @setting.error
    async def setting_error(self, context, error):
        if isinstance(error, discord.ext.commands.errors.MissingPermissions):
            return await context.send( context.message.author.mention + ', ' + str(error) )
        else:
            print(error)



def setup(bot):
    bot.add_cog(Setting(bot))