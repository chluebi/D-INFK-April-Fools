import discord
import logging

import asyncio

from discord_user import DiscordUser


functions_to_trigger = set()
already_added = set()

bot = [None]

# sets the bot object
def setup(b):
    bot[0] = b


def on_score_update(func):
    if func.__name__ in already_added:
        return
    already_added.add(func.__name__)
    functions_to_trigger.add(func)
    return func

# everytime the score is updated, all methods with the on_score_update
# decorator are also triggered
async def score_update(member: discord.Member, user: DiscordUser, delta_score: int, reason):
    logging.info("event fire")
    loop = asyncio.get_event_loop()
    for f in functions_to_trigger:
        loop.create_task(f(bot[0], member, user, delta_score, reason))
