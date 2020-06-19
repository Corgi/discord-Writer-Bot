import discord, lib
from discord.ext import commands
from structures.user import User
from structures.wrapper import CommandWrapper


class Todo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="todo")
    @commands.guild_only()
    async def todo(self, context):
        """
        Displays current TODO list
        """
        user = User(context.message.author.id, context.guild.id, context)

        todo = lib.get_asset('todo', user.get_guild())

        output = '```ini\n'

        for type in todo.keys():

            output += '********** ' + lib.get_string('todo:' + str(type), user.get_guild()) + ' **********\n'

            items = todo[type]
            if len(items):

                n = 1

                for item in items:
                    output += str(n) + '. ' + item + '\n'
                    n += 1
            else:
                output += '-'

            output += '\n\n'

        output += '```'

        return await context.send(output)


def setup(bot):
    bot.add_cog(Todo(bot))