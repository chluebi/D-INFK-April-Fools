import asyncio

import discord
from discord.ext import commands

from events import on_score_update, score_update

# This file is meant to be easily copyable and as a quick introduction to how nextcord works


class Cog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

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

    # message listener
    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        # do something with the message here

    # triggers the on_score_update event
    @commands.command()
    async def event(self, ctx):
        await score_update(ctx.message.author, 100)
    
    # gets triggered with the on_score_update event
    @on_score_update
    async def foobar(bot, user, new_score):
        channel = bot.get_channel(954423559600631832)
        await channel.send(f"{str(user)}'s score was changed to {new_score}")


# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Cog(bot))
