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
    @commands.command(name='loadusers')
    @commands.has_permissions(administrator=True)
    async def load_users(self, ctx):
        

        for member in ctx.guild.members:
            db_user = self.db.get_discord_user(member.id)
        
            if db_user is None:
                #await ctx.channel.send(f"unknown user {member.name} creating")
                #TODO check Name and Nick
                self.db.create_discord_user(member.id, member.name, 1000, member.bot, False)
                
                await ctx.channel.send(f"{member.name} created")


    # enforce naming
    @commands.command(name='enforcenames')
    @commands.has_permissions(administrator=True)
    async def enforce_names(self, ctx):
        try:
            for member in ctx.guild.members:
                db_user = self.db.get_discord_user(member.id)


            
                if db_user is None:
                    #await ctx.channel.send(f"unknown user {member.name} creating")
                    #TODO check Name and Nick

                    
                    db_user = self.db.create_discord_user(member.id, member.name, 1000, member.bot, False)
                    
                    await ctx.channel.send(f"{member.name} created")
                
                credits = str(db_user.social_credit)
                
                nick = f'{member.name[:25]} [{credits}]'

        

                result = await member.edit(nick=nick)


        except Exception as e:
            print(e)
    
    # restore names
    @commands.command(name='restorenames')
    @commands.has_permissions(administrator=True)
    async def restore_names(self, ctx):
        
        try:
            for member in ctx.guild.members:
                db_user = self.db.get_discord_user(member.id)

                print(db_user)
                print(member)
            
                if db_user is None:
                    #await ctx.channel.send(f"unknown user {member.name} creating")
                    #TODO check Name and Nick

                    print(member)
                    db_user = self.db.create_discord_user(member.id, member.name, 1000, member.bot, False)
                    
                    await ctx.channel.send(f"{member.name} created")
                

                
                nick = db_user.old_name

                print(nick)

                result = await member.edit(nick=nick)
                print(result)

        except Exception as e:
            print(e)



    # db test
    @commands.command(name='dbtest')
    @commands.has_permissions(administrator=True)
    async def db_test(self, ctx):
        
        self.db.initalize_tables()

        self.db.get_discord_user(1)
        await ctx.channel.send(f'db connected')

    # db test
    @commands.command(name='sql')
    @commands.has_permissions(administrator=True)
    async def sql_query(self, ctx, *, query):
        result = self.db.sql_query(query)

        await ctx.channel.send(result[:2000])


    # credits test
    @commands.command(name='credits')
    @commands.has_permissions(administrator=True)
    async def db_test(self, ctx):

        db_user = self.db.change_credits(ctx.author.id, TransactionType.birthday_wish, ctx.message.id, ctx.channel.id, reason="Test credits")
        # TODO Check None
        await ctx.channel.send(f'credits test {ctx.author.name} has {db_user.social_credit}')



    # message listener
    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)

        db_user = self.db.get_discord_user(message.author.id)
        
        if db_user is None:
            #TODO check Name and Nick
            self.db.create_discord_user(message.author.id, message.author.name, 1234, message.author.bot, False)
            
            await ctx.channel.send(f"{message.author.name} created")


    # triggers the on_score_update event
    @commands.command()
    async def event(self, ctx):
        db_user = self.db.get_discord_user(ctx.message.author.id)
        await score_update(ctx.message.author, db_user, 0, "Event was triggered")
    
    # gets triggered with the on_score_update event
    @on_score_update
    async def foobar(bot, member, user, delta_score, reason):
        channel = bot.get_channel(954423559600631832)
        await channel.send(f"{str(member)}'s score was changed to {user.social_credit}")


# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Cog(bot))
