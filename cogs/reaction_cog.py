import asyncio

import discord
import events
from discord.ext import commands
from db import SQLiteDBManager

from bot import discord_config

from constants import TransactionType


#ETH server emote ids
#                  thx                  this                aww                 santaawww
GOOD_EMOTE_IDS = [807968281507659776, 747783377662378004, 810266232061952040, 910435057607524352]
#                   that                yikes               mike_bruh           bruh
BAD_EMOTE_IDS = [758262252699779073, 851469747643220048, 937352413810151424, 747783377159061545]
TA_APPROVED = 893967315996143616



class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    #when one reacts with good emotes they give Social Credit Score, remove some when bad reaction
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member is not None:
            #ReactionUp Transaction
            if any(payload.emoji.id == s for s in GOOD_EMOTE_IDS):
                messenger = get_author(payload)
                self.db.change_credits(payload.member, TransactionType.reaction_good, payload.message_id, payload.channel_id)
            elif any(payload.emoji.id == s for s in BAD_EMOTE_IDS):
                #ReactionDown Transaction
                messenger = get_author(payload)
                self.db.change_credits(payload.member, TransactionType.reaction_bad, payload.message_id, payload.channel_id)
            elif payload.emoji.id == TA_APPROVED:
                messenger = get_author(payload)
                self.db.change_credits(payload.member, TransactionType.TAApproved, payload.message_id, payload.channel_id)

def get_author(payload):
    return payload.member.guild.get_channel(payload.channel_id).fetch_message(payload.message_id).author            

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Reaction(bot))
    