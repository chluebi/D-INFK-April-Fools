import asyncio

import discord

from discord.ext import commands
from db import SQLiteDBManager
from db import DiscordUser

from constants import TransactionType
from events import on_score_update, score_update

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

            
    #Gives user timeout
    @on_score_update
    async def timeout(self, member: discord.Member, user: DiscordUser, delta_score: int, reason):
        if user.social_credit > 0 or member.guild_permissions.administrator:
            return
        
        channel = member.guild.get_channel(954423559600631832)
        await channel.send(f'timeout: {member.id} This is a timeout for {member.mention}')
        amount = -1 * user.social_credit + 250
        await self.db.change_credits(member, TransactionType.timeout, amount=amount, reason="Timeout")

## simply here cause its considered a cog
def setup(bot):
    pass
