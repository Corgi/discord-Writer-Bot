import asyncio
import lib

class CommandWrapper:

    TIMEOUT_WAIT=30

    def __init__(self):
        self._arguments = []

    async def check_arguments(self, context, **kwargs):

        # Loop through the arguments we defined in the __init__ of the command class
        for arg in self._arguments:

            # If we found that argument in the arguments passed through in the command check, then we can check it
            if arg['key'] in kwargs:

                # Get the value passed into this function for checking
                value = kwargs[arg['key']]

                # If the argument is required and the value is invalid, then prompt for a value
                if arg['required'] and not value:

                    response = await self.prompt(context, arg)
                    if response:
                        # Set the content back into the keyword arguments to be accessed from the calling command
                        kwargs[arg['key']] = response.content
                        value = kwargs[arg['key']]
                    else:
                        return False

                # We got a response, now do we need to check the type or do any extra content checks?
                if not await self.check_content(arg, value, context):
                    return False


        return kwargs

    async def check_content(self, argument, content, context):

        result = True

        # Do we need to check the type?
        # The only type checking we do is str or int, as that's basically all they can supply.
        # Assumption is that str is anything that is not a number.
        if 'type' in argument and argument['type'] is int and not lib.is_number(content):
            result = False
        elif 'type' in argument and argument['type'] is str and lib.is_number(content):
            result = False

        # Do we need to do any extra checks?
        if 'check' in argument and callable(argument['check']):
            content = str(content).lower()
            if not argument['check'](content):
                result = False

        # If the result is false and the argument specifies an error message, send that.
        if result is False and 'error' in argument:
            await context.send( context.message.author.mention + ', ' + lib.get_string(argument['error'], context.guild.id) )

        return result


    async def prompt(self, context, argument, raw_message=False, timeout=None):

        # Get the message we want to use for the prompt
        message = argument['prompt']

        # Use default timeout is none specified
        if timeout is None:
            timeout = self.TIMEOUT_WAIT

        # Send the prompt message and wait for a reply
        if not raw_message:
            message = lib.get_string(message, context.guild.id)

        # Define the function we use to check the value
        def _check(msg):
            return msg.author == context.author and msg.channel == context.channel and not msg.content.startswith(context.prefix)

        # Send the prompt message asking for the argument and await response
        req = await context.send(f'{context.author.mention}, {message}')
        try:
            response = await self.bot.wait_for('message', check=_check, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            await req.edit(content=lib.get_string('req:timeout', context.guild.id))
            return False


    async def adhoc_prompt(self, context, argument, raw_message=False, timeout=None):
        """
        This should be called if the prompt is being done manually in the code, instead of being used against the array of self.arguments
        :param context:
        :param argument:
        :param raw_message:
        :param timeout:
        :return:
        """
        response = await self.prompt(context, argument, raw_message, timeout)
        if not response:
            return False

        # We got a response, now do we need to check the type or do any extra content checks?
        if not await self.check_content(argument, response.content, context):
            await context.send( context.author.mention + ', ' + lib.get_string('err:cmdoptions', context.guild.id))
            return False

        return response

    async def split_send(self, context, user, message):
        """
        Send a long message (more than 2000 characters) by splitting it into several messages.
        :param context:
        :param user:
        :param message:
        :return:
        """

        # We'll do a shorter limit, just to give us some leeway.
        max = 1750

        # Split the message by newline characters.
        split = message.split('\n')
        count = len(split)
        content = ''
        i = 1

        for line in split:

            # Add the line to the current content, and then see if that takes us over the limit.
            check = content + line + '\n'
            if len(check) > max or i >= count:

                # Send first part of message
                await context.send(user.get_mention() + ', ' + content)

                # Then start again with a new current message
                content = line

            else:
                # No, carry on.
                content = check

            i += 1