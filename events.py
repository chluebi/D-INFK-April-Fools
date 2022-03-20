import discord
from typing import Union

from db import DiscordUser

functions_to_trigger = set()

bot = [None]

# sets the bot object
def setup(b):
    bot[0] = b


def on_score_update(func):
    functions_to_trigger.add(func)
    return func

# everytime the score is updated, all methods with the on_score_update
# decorator are also triggered
async def score_update(member: discord.Member, user: DiscordUser, delta_score: int, reason):
    for f in functions_to_trigger:
        await f(bot[0], member, user, delta_score, reason)
        
"""
import discord
from typing import Union


functions_to_trigger = set()

bot = [None]

# sets the bot object
def setup(b):
    bot[0] = b


def on_score_update(func):
    functions_to_trigger.add(func)
    return func

# everytime the score is updated, all methods with the on_score_update
# decorator are also triggered
async def score_update(user: Union[discord.User, discord.Member], new_score: int):
    for f in functions_to_trigger:
        await f(bot[0], user, new_score)
"""