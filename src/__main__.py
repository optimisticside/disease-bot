"""Disease diagnoser bot
Tries its best to diagnose what medical conditions the user
may have based on what symptoms they provide. Also provides information
about diseases, such as their symptoms and possible treatments.

Please note that this bot is not in no way a proper medical diagnosis
and anyone in need of a diagnosis should consult a physician.

2022 EVHS Programming Club Hackathon
Vijay Sharma, Pranav Kunnath, Hansel Puthenparambil, Akash Agarwal
4/2/2022
See LICENSE for further details
"""

import sys
import json
from typing import List, Dict, Tuple, Optional
import discord


PREFIX = "?"
RESULT_COUNT = 5
DISCLAIMER = (
    "Please note that this result is in no way a proper diagnosis.\n"
    "Consult a physician for a diagnosis."
)


Database = Dict[str, List[List[str]]]


if "--nouvloop" not in sys.argv:
    import uvloop

    uvloop.install()


async def handle_command(
    message: discord.Message, database: Database, command: str, args: str
):
    """Handles a command given to the bot by a user."""
    if message.author.bot or not message.guild:
        return

    # Our database will be a key-value database where the
    # key is a string representing the name of the disease, and
    # the value is going to be an array of symptoms.
    if command == "diagnose":
        # We want to provide the most likely diseases, so we
        # store a array of tuples with the disease name and the
        # number of matched symptoms.
        diseases: List[Tuple[str, int]] = []
        given = [x.lower() for x in args]

        for (name, data) in database.items():
            symptoms, *_ = data
            # We rank diseases' likeliness by how many of the
            # symptoms you have that are not a symptom of it.
            # 
            # We also want to account for how many symptoms were provided,
            # since if a disease has only 1 symptom provided and none of them
            # match, then the rank will be 1, which is quite low compared to some
            # other diseases with many pre-defined symptoms. This is why we divide
            # by the number of symptoms to reduce our bias.
            rank = len([x for x in symptoms if x not in given]) / len(symptoms)
            diseases.append((name, rank))

        diseases.sort(reverse=False, key=lambda x: x[1])
        result = ", ".join(x[0] for x in diseases[0:RESULT_COUNT])
        await message.reply(f"You might have: {result}\n{DISCLAIMER}")

    elif command == "info":
        # this is for u akash
        name = args[0].lower()

        if not name in database:
            return await message.reply(f"{name} is was not found in the database.")

        disease = database[name]
        symptoms = ", ".join(disease[0])
        treatements = ", ".join(disease[1])
        await message.reply(
            f"Symptoms for {name} include: {symptoms}\nTreatements include: {treatements}."
        )

    elif command == "help":
        await message.reply(f"Say `{PREFIX}diagnose` for me to diagnose something.")


def main(args: List[str]):
    """Main program entry point. Takes in arguments
    under the asusmption that the program has been removed
    from the arguments before being given to this subroutine.
    """
    if len(args) < 2:
        print("Invalid arguments provided.", file=sys.stderr)
        return

    with open(args[1], "r", encoding="utf-8") as database_file:
        database = json.load(database_file)
        bot = discord.Client()

        @bot.event
        async def on_message(message: discord.Message):
            prefix: Optional[str] = None
            for possible_prefix in [PREFIX, f"<@{bot.user.id}>"]:
                if message.content.startswith(possible_prefix):
                    prefix = possible_prefix
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
    main(sys.argv[1:])
