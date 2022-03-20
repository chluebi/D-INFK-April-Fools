import asyncio
import discord
import events
from discord.ext import commands
from db import SQLiteDBManager
from bot import discord_config
from constants import TransactionType
from profanity_check import predict, predict_prob

class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.cutoff = 0.5
        #just an arbitrary value, needs testing

    
    @commands.Cog.listener()
    async def on_message(self, payload):
        prob = predict_prob(payload.content)
        if(prob >= self.cutoff):
            messenger = payload.member.guild.get_channel(payload.channel_id).fetch_message(payload.message_id).author
            self.db.change_credits(payload.member, TransactionType.profanity, payload.message_id, payload.channel_id)


def setup(bot: commands.Bot):
    bot.add_cog(Reaction(bot))