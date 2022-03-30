import asyncio
import discord
import events
from discord.ext import commands
from db import SQLiteDBManager
from bot import discord_config
from constants import TransactionType
from profanity_check import predict, predict_prob

class profanity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.cutoff = 0.5
        #just an arbitrary value, needs testing

    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        prob = predict_prob([message.content])[0]
        if(prob >= self.cutoff):
            self.db.change_credits(message.author, TransactionType.profanity, message.id, message.channel.id)


def setup(bot: commands.Bot):
    bot.add_cog(profanity(bot))