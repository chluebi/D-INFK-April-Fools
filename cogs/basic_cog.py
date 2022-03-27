import asyncio

import discord
from discord.ext import commands
from db import SQLiteDBManager
from db import DiscordUser

from bot import discord_config

from constants import TransactionType

from events import on_score_update, score_update

import traceback


# This file is meant to be easily copyable and as a quick introduction to how nextcord works


class Cog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

    # basic command
    @commands.command(name='ping')
    async def ping(self, ctx, message: str = "Default message"):
        await ctx.channel.send(f'{ctx.author.mention}, pong! {message}')

    # basic mod command
    # mods can probably manage channels so this is used as a proxy for that
    @commands.command(name='mod-ping')
    @commands.has_permissions(manage_channels=True)
    async def mod_ping(self, ctx):
        await ctx.channel.send(f'{ctx.author.mention}, you are a mod :)')

    # basic admin command
    @commands.command(name='admin-ping')
    @commands.has_permissions(administrator=True)
    async def admin_ping(self, ctx):
        await ctx.channel.send(f'{ctx.author.mention}, you are an admin :)')


    # db test
    @commands.command(name='transactions')
    async def get_transactions(self, ctx):
        
        server_id = self.db.get_key("DiscordServerId")

        transactions = self.db.get_last_transactions(ctx.author.id, 10)
        embed=discord.Embed(title=f"Social credit history of {ctx.author.display_name}")
        embed.set_author(name=ctx.author.display_name)

        description = """**Your last transactions**""" + "\r\n"
        for transaction in transactions:

            if transaction.discord_channel_id is not None and transaction.discord_message_id is not None:
                link = f"https://discord.com/channels/{server_id}/{transaction.discord_channel_id}/{transaction.discord_message_id}"
                entry = f'ID:{transaction.id} [{transaction.type_name}]({link}) at {transaction.date_time} for {transaction.amount} Credits Reason: {transaction.reason[:100]}'
                description += entry + "\r\n"
            else:
                entry = f'ID:{transaction.id} **{transaction.type_name}** at {transaction.date_time} for {transaction.amount} Credits Reason: {transaction.reason[:100]}'
                description += entry + "\r\n"


        embed.description = description
        #for transaction in transactions:
        #    embed.add_field(name="Entry", value="", inline=False)
        await ctx.send(embed=embed)




    # credits test
    @commands.command(name='credits')
    @commands.has_permissions(administrator=True)
    async def db_test(self, ctx):
        print(ctx.channel.id)
        db_user = await self.db.change_credits(ctx.author, TransactionType.birthday_wish, discord_message_id=ctx.message.id, discord_channel_id=ctx.channel.id, reason="Test credits")
        # TODO Check None
        await ctx.channel.send(f'credits test {ctx.author.display_name} has {db_user.social_credit}')



    # message listener
    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        db_user = self.db.get_discord_user(message.author.id)
        
        if db_user is None:
            #TODO check Name and Nick
            self.db.create_discord_user(message.author.id, message.author.display_name, 1000, message.author.bot, False)
            await ctx.channel.send(f"{message.author.display_name} created")

        words_1984 = ["1984", "literarisch", "neunzehnhundertvierundachtzig"]


        # using list comprehension
        # checking if string contains list element
        if [ele for ele in words_1984 if(ele in message.content)]:
            await self.db.change_credits(message.author, TransactionType.mention_1984, ctx.author.id,
            ctx.message.id, ctx.channel.id, None, f"Mentioned 1984")
            await ctx.channel.send(f"You are using not allowed mentions")

    # triggers the on_score_update event
    @commands.command()
    async def event(self, ctx, delta_score = 0):
        db_user = self.db.get_discord_user(ctx.message.author.id)
        await score_update(ctx.message.author, db_user, delta_score, "Event was triggered")
    
    # gets triggered with the on_score_update event
    @on_score_update
    async def foobar(bot, member, user, delta_score, reason):
        changelog_channel_id = bot.db.get_key("ChangelogChannelId")
        channel = bot.get_channel(changelog_channel_id)
        await channel.send(f"{str(member)}'s score was changed by {delta_score}")


# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Cog(bot))
