import discord
from discord.ext import commands
from constants import TransactionType

class Judge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @commands.command()
    @commands.has_any_role(957344554569310239, 957592832108011580)  # judge role on test and main server
    @commands.cooldown(1, 120, commands.BucketType.member)
    @commands.guild_only()
    async def judge(self, ctx, member: discord.Member, score_update = 0):
        #spam botfun (general on test server) 
        if ctx.channel.id != 768600365602963496 and ctx.channel.id != 747776646551175217 and ctx.channel.id != 954423559600631832:
            return
        if member is None:
            await ctx.reply("No victim chosen to judge.", delete_after=10)
            return
        if member.id == ctx.author.id:
            await ctx.reply("It is illegal to change your own score! -50 for even trying!")
            await self.db.change_credits(member, TransactionType.judge_manual, ctx.message.id, ctx.channel.id, amount=-50, reason="Tried to increase their own score")
            return
        if score_update == 0:
            await ctx.reply("Changing the score by 0 doesn't make any sense.", delete_after=10)
            return
        if score_update < -20:
            score_update = -20
        if score_update > 20:
            score_update = 20
        await self.db.change_credits(member, TransactionType.judge_manual, ctx.message.id, ctx.channel.id, amount=score_update, reason="A judge wanted to")
        await ctx.reply(f"Successfully changed the score of {str(member)}")


def setup(bot: commands.Bot):
    bot.add_cog(Judge(bot))
