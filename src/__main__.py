# 2022 EVHS Programming Club Hackathon
# Vijay Sharma, Pranav Kunnath, Hansel Puthenparambil, Akash Agarwal
# 4/2/2022
# See LICENSE for further details

import discord
import asyncio
import json
import sys

PREFIX = "?"
RESULT_COUNT = 5


if not '--nouvloop' in sys.argv:
    import uvloop
    uvloop.install()


async def handle_command(message, database, command, args):
    """Handles a command given to the bot by a user.
    """
    if message.author.bot or not message.guild:
        return

    # Our database will be a key-value database where the
    # key is a string representing the name of the disease, and
    # the value is going to be an array of symptoms.
    if command == "diagnose":
        # We want to provide the most likely diseases, so we
        # store a array of tuples with the disease name and the
        # number of matched symptoms.
        diseases = []
        given = [x.lower() for x in args]

        for (disease, data) in database.items():
            symptoms, *_ = data
            diseases.append((disease, len([x for x in symptoms if not x in given])))

        diseases.sort(reverse=True, key=lambda x: x[1])
        result = ", ".join(x[0] for x in diseases[1:RESULT_COUNT])
        await message.reply(f"You might have: {result}")

    elif command == "info":
        # this is for u akash
        name = args[0].lower()

        if not name in database:
            return await message.reply(f"{name} is was not found in the database.")

        disease = database[name]
        symptoms = ", ".join(disease[0])
        treatements = ", ".join(disease[1])
        await message.reply(f"Symptoms for {name} include: {symptoms}\nTreatements include: {treatements}.")

    elif command == "help":
        await message.reply(f"Say `{PREFIX}diagnose` for me to diagnoze seomthing.")


def make_database(path):
    """Opens the database file.
    Returns None if not found.
    """
    with open(path) as f:
        return json.load(f)


def __main__(args):
    """Main program entry point. Takes in arguments
    under the asusmption that the program has been removed
    from the arguments before being given to this subroutine.
    """
    if len(args) < 2:
        return print("Invalid arguments provided.", file=sys.stderr)

    database = make_database(args[1])
    bot = discord.Client()

    if database is None:
        return print("Unable to open database file. Check file permissions.", file=sys.stderr)

    @bot.event
    async def on_message(message: discord.Message):
        prefix: Optional[str] = None
        for p in [PREFIX, f"<@{bot.user.id}>"]:
            if message.content.startswith(p):
                prefix = p
                break

        if prefix is not None and message.content != prefix:
            async with message.channel.typing():
                content = message.content[len(prefix) :].strip()
                if len(content) < 1:
                    return

                (command, *args) = content.split(" ")
                await handle_command(message, database, command, args)

    @bot.event
    async def on_ready():
        print("Connected to Discord")

    bot.run(args[0])


if __name__ == "__main__":
    __main__(sys.argv[1:])
