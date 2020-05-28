import asyncio
import lib

class CommandWrapper:

    TIMEOUT_WAIT=10

    def __init__(self):
        self._arguments = []
        pass

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
                        kwargs[arg['key']] = response.content
                    else:
                        return False

        return kwargs

    async def prompt(self, context, argument, raw_message=False, timeout=None):

        # Get the message we want to use for the prompt
        message = argument['prompt']

        # Get any extra check we want to do for this argument, to check the value is in a specific format
        extra_check = argument['check'] if 'check' in argument else False

        # Use default timeout is none specified
        if timeout is None:
            timeout = self.TIMEOUT_WAIT

        # Check if the response is from the same user, in the same channel.
        def check_message(msg):
            return msg.author == context.author and msg.channel == context.channel and not msg.content.startswith(context.prefix)

        # Store the name of the function to call in the variable 'call_check'
        call_check = check_message

        # If we specified an extra check, we want to check that as well.
        if callable(extra_check):

            # If the extra_check is a lambda, then define a new function to use in the response check
            def check_message_extra(msg):
                return check_message(msg) and extra_check(msg.content.lower())

            # And then assign it to the 'call_check' variable
            call_check = check_message_extra

        # Send the prompt message and wait for a reply
        if not raw_message:
            message = lib.get_string(message, context.guild.id)

        req = await context.send(f'{context.author.mention}, {message}')
        try:
            response = await self.bot.wait_for('message', check=call_check, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            await req.edit(content='Request for response timed out')
            return False

# @commands.command()
# async def foo(ctx, bar=None):
#   if bar is None:
#     req = await ctx.send(f'{ctx.author.mention}: please supply arg bar')
#     try:
#       msg = await ctx.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
#     except asyncio.TimeoutError:
#       await req.edit(content='Request for arg bar timed out')
#       return
#     bar = msg.content
#   ...  # rest of command