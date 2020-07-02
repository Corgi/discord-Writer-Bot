import discord, lib, math
from discord.ext import commands
from structures.user import User
from structures.wrapper import CommandWrapper

class Project(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self._supported_commands = ['create', 'delete', 'rename', 'update', 'view', 'complete', 'restart', 'finish', 'uncomplete', 'list']
        self._arguments = [
            {
                'key': 'cmd',
                'prompt': 'project:argument:cmd',
                'required': True,
                'check': lambda content: content in self._supported_commands,
                'error': 'project:err:argument:cmd'
            }
        ]

    @commands.command(name="project")
    @commands.guild_only()
    async def project(self, context, cmd=None, *opts):
        """
        The project command allows you to create different projects and store word counts against them separately. They also integrate with the `wrote` and `sprint` commands, allowing you to define words written against a chosen project. (See the help information for those commands for more info).

        Examples:
            `project create sword The Sword in the Stone` - Creates a new project with the shortname "sword" (used to reference the project when you want to update it), and the full title "The Sword in the Stone".
            `project delete sword` - Deletes the project with the shortname "sword"
            `project rename sword sword2 The Sword in the Stone Two` - Renames the project with the shortname "sword" to - shortname:sword2, title:The Sword in the Stone Two (If you want to keep the same shortname but change the title, just put the same shortname, e.g. `project rename sword sword The Sword in the Stone Two`.
            `project update sword 65000` - Sets the word count for the project with the shortname "sword" to 65000.
            `project view` - Views a list of all your projects.
            `project complete sword` - Marks your project with the shortname "sword" as completed.
            `project restart sword` - Marks your project with the shortname "sword" as not completed.
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Check the arguments were all supplied and get a dict list of them and their values, after any prompts
        args = await self.check_arguments(context, cmd=cmd)
        if not args:
            return

        # Overwrite the variables passed in, with the values from the prompt and convert to lowercase
        cmd = args['cmd'].lower()

        # Make sure some options have been sent through
        if len(opts) == 0 and cmd != 'view' and cmd != 'list':
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:options', user.get_guild()))

        # Check which command is being run and run it.
        # Since the options can have spaces in them, we need to send the whole thing through as a list and then work out what is what in the command.
        if cmd == 'create':
            return await self.run_create(context, opts)
        elif cmd == 'delete':
            return await self.run_delete(context, opts)
        elif cmd == 'rename':
            return await self.run_rename(context, opts)
        elif cmd == 'update':
            return await self.run_update(context, opts)
        elif cmd == 'view' or cmd == 'list':
            return await self.run_view(context)
        elif cmd == 'complete' or cmd == 'finish':
            return await self.run_complete(context, opts)
        elif cmd == 'restart' or cmd == 'uncomplete':
            return await self.run_restart(context, opts)

    async def run_restart(self, context, opts):
        """
        Mark a project as not completed
        :param context:
        :param opts:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        shortname = opts[0].lower()

        # Make sure the project exists.
        project = user.get_project(shortname)
        if not project:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:noexists', user.get_guild()).format(shortname))

        project.uncomplete()
        return await context.send(user.get_mention() + ', ' + lib.get_string('project:uncompleted', user.get_guild()))

    async def run_complete(self, context, opts):
        """
        Mark a project as completed
        :param context:
        :param opts:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        shortname = opts[0].lower()

        # Make sure the project exists.
        project = user.get_project(shortname)
        if not project:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:noexists', user.get_guild()).format(shortname))

        already_completed = project.is_completed()
        project.complete()

        # Was this the first time they completed it?
        if already_completed == 0:

            # Calculate how much XP to give them (1xp per 100 words). Min 10. Max 5000.
            xp = math.ceil(project.get_words() / 100)
            if xp < 10:
                xp = 10
            elif xp > 5000:
                xp = 5000

            # Give them the xp and print the message.
            await user.add_xp(xp)
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:completed', user.get_guild()).format(project.get_title(), xp))

        else:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:recompleted', user.get_guild()))

    async def run_view(self, context):
        """
        View a list of the user's projects
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        projects = user.get_projects()

        # If they have no projects, then we can't display them.
        if not projects:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:noprojects', user.get_guild()))

        message = ''

        for project in projects:

            if project.is_completed():
                message += ':sparkler: '

            message += '**'+project.get_name()+'** ('+project.get_shortname()+')\n'
            message += lib.get_string('wordcount', user.get_guild()) + ': ' + str(project.get_words()) + '\n\n'

        # Project lists can get very long. If it is over 2000 characters, we need to split it.
        if len(message) >= 2000:
            return await self.split_send(context, user, lib.get_string('project:list', user.get_guild()) + message)
        else:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:list', user.get_guild()) + message)

    async def run_update(self, context, opts):
        """
        Update a project's word count
        :param context:
        :param opts:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        shortname = opts[0].lower()
        amount = opts[1] if len(opts) > 1 else None

        # Make sure the amount is valid.
        amount = lib.is_number(amount)
        if not amount:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:amount', user.get_guild()))

        # Make sure the project exists.
        project = user.get_project(shortname)
        if not project:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:noexists', user.get_guild()).format(shortname))

        # Is it already completed?
        if project.is_completed():
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:alreadycompleted', user.get_guild()).format(shortname))

        # Update the word count.
        project.update(amount)
        return await context.send(user.get_mention() + ', ' + lib.get_string('project:updated', user.get_guild()).format(amount, project.get_name(), project.get_shortname()))

    async def run_rename(self, context, opts):
        """
        Rename a project
        :param context:
        :param opts:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        original_shortname = opts[0].lower()
        new_shortname = opts[1].lower()
        new_title = " ".join(opts[2:])

        # Make sure the project exists
        project = user.get_project(original_shortname)
        if not project:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:noexists', user.get_guild()).format(original_shortname))

        # Make sure they don't already have one with that new shortname.
        project_with_new_shortname = user.get_project(new_shortname)
        if project_with_new_shortname is not None and project_with_new_shortname.get_id() != project.get_id():
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:exists', user.get_guild()).format(new_shortname))

        # Get the original title.
        original_title = project.get_name()

        # Rename it.
        project.rename(new_shortname, new_title)
        return await context.send(user.get_mention() + ', ' + lib.get_string('project:renamed', user.get_guild()).format(original_title, original_shortname, new_title, new_shortname))


    async def run_delete(self, context, opts):
        """
        Try to delete a project with the given shortname
        :param context:
        :param opts:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Make sure the project exists first
        shortname = opts[0].lower()
        project = user.get_project(shortname)
        if not project:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:noexists', user.get_guild()).format(shortname))

        # Delete it.
        project.delete()
        return await context.send(user.get_mention() + ', ' + lib.get_string('project:deleted', user.get_guild()).format(project.get_name(), project.get_shortname()))

    async def run_create(self, context, opts):
        """
        Try to create a project with the given names
        :param context:
        :param shortname:
        :param title:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Get the shortname and title out of the argument list.
        shortname = opts[0].lower()
        title = " ".join(opts[1:]) # Every argument after the first one, joined with spaces.

        # Make sure the shortname and title are set.
        if len(shortname) == 0 or len(title) == 0:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:names', user.get_guild()))

        # Make sure they don't already have a project with this shortname
        project = user.get_project(shortname)
        if project is not None:
            return await context.send(user.get_mention() + ', ' + lib.get_string('project:err:exists', user.get_guild()).format(shortname))

        # Create the project
        user.create_project(shortname, title)
        return await context.send(user.get_mention() + ', ' + lib.get_string('project:created', user.get_guild()).format(title, shortname))


def setup(bot):
    bot.add_cog(Project(bot))