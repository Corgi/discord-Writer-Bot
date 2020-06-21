import lib, random, re, string

class NameGenerator:

    MAX_AMOUNT = 25
    DEFAULT_AMOUNT = 10
    MAX_RETRIES = 10

    def __init__(self, type, context):
        self.type = type
        self.context = context
        self._last = ''

    def generate(self, amount):

        generated_names = []

        # If the amount if higher than the max, set it to the max
        if amount > self.MAX_AMOUNT:
            amount = self.MAX_AMOUNT

        # If it's less than 1 for any reason, just use the default
        if amount is None or amount < 1:
            amount = self.DEFAULT_AMOUNT

        # # If the type is 'idea' or 'prompt', change the amount to 1, as that will take up too much space.
        # if self.type == 'idea' or self.type == 'prompt':
        #     amount = 1

        asset_file = 'gen_' + self.type
        source = lib.get_asset(asset_file, self.context.guild.id)
        retry_attempts = 0

        # If we loaded the asset source okay, then let's loop through and generate some responses
        if source:

            # Store all the name choices before we start the loop
            choices = source['names']

            def replace(match):

                match = match.group().replace('$', '')

                if match in choices.keys():

                    # Generate a choice
                    choice = random.choice(choices[match])

                    i = 0

                    # Make sure it's not the same as the last one.
                    # Only try a maximum of self.MAX_RETRIES times though, we don't want a situation where an infinite loop could happen
                    while len(choice) > 2 and choice == self._last and i < self.MAX_RETRIES:
                        i += 1
                        choice = random.choice(choices[match])

                    self._last = choice
                    return choice
                else:
                    self._last = match
                    return match


            # Loop as many times as the amount we requested, and build up a generated name for each
            x = 0
            while x < amount:

                x += 1

                # Get the formats from the source data
                formats = source['formats']

                # Pick a random one to use
                format = random.choice(formats)

                # Variable to store the last chosen element, so we don't have the same thing twice in a row
                self._last = ''

                # Generate a name
                name = re.sub(r"\$([a-z0-9]+)", replace, format)

                # If we've already had this exact one, try again, up to self.MAX_RETRIES times
                if name in generated_names and retry_attempts < self.MAX_RETRIES:
                    x -= 1
                    retry_attempts += 1
                else:
                    # Add it to the return array
                    generated_names.append(name)
                    retry_attempts = 0

        # Sort the results alphabetically
        generated_names.sort()

        # Uppercase the first letter of each word, if it's anything but idea generation or prompt generatio
        if self.type != 'idea' and self.type != 'prompt':
            generated_names = map(lambda el : string.capwords(el), generated_names)

        # Generate the message
        message = lib.get_string('generate:message', self.context.guild.id).format(
            amount,
            lib.get_string('generate:type:' + self.type, self.context.guild.id)
        )

        return {
            'names': generated_names,
            'message': message
        }