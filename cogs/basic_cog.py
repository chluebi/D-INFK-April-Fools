import discord
from discord.ext import commands

from constants import TransactionType

import traceback


# This file is meant to be easily copyable and as a quick introduction to how nextcord works


class Cog(commands.Cog):
    words_1984 = {"1984", "literarisch", "neunzehnhundertvierundachtzig"}

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

    # left in to quickly see that bot still alive
    # basic mod command
    # mods can probably manage channels so this is used as a proxy for that
    @commands.command(name='ping')
    @commands.has_permissions(manage_channels=True)
    async def mod_ping(self, ctx):
        await ctx.channel.send(f'{ctx.author.mention}, I am still alive :)')

    # db test
    @commands.command(name='transactions')
    async def get_transactions(self, ctx, member: discord.Member = None):
        if ctx.channel.id != 768600365602963496 and ctx.channel.id != 747776646551175217 and ctx.channel.id != 954423559600631832:
            return

        if member is None:
            member = ctx.message.author
        server_id = self.db.get_key("DiscordServerId")

        user = self.db.get_discord_user(member.id)
        transactions = self.db.get_last_transactions(member.id, 10)
        embed = discord.Embed(
            title=f"Social credit history of {member.display_name}")
        embed.set_author(name=member.display_name,
                         icon_url=str(member.avatar_url))
        embed.set_thumbnail(url=(member.avatar_url))

        reason = transaction.reason
        if reason is None:
            reason = "n/a"

        description = f"""**Your current credit balance is {user.social_credit}**""" + "\r\n"
        for transaction in transactions:
            if transaction.discord_channel_id is not None and transaction.discord_message_id is not None:
                link = f"https://discord.com/channels/{server_id}/{transaction.discord_channel_id}/{transaction.discord_message_id}"
                entry = f'ID: {transaction.id} [{transaction.type_name}]({link}) at {transaction.time} for {transaction.amount} Credits **Reason**: {reason[:100]}'
                description += entry + "\r\n"
            else:
                entry = f'ID: {transaction.id} **{transaction.type_name}** at {transaction.time} for {transaction.amount} Credits **Reason**: {reason[:100]}'
                description += entry + "\r\n"

        """
        while len(transactions) > 0:

            field_value = ""

            for transaction in transactions[5:]:
                if transaction.discord_channel_id is not None and transaction.discord_message_id is not None:
                    link = f"https://discord.com/channels/{server_id}/{transaction.discord_channel_id}/{transaction.discord_message_id}"
                    entry = f'ID:{transaction.id} [{transaction.type_name}]({link}) at {transaction.date_time} for {transaction.amount} Credits Reason: {transaction.reason[:100]}'
                    field_value += entry + "\r\n"
                else:
                    entry = f'ID:{transaction.id} **{transaction.type_name}** at {transaction.date_time} for {transaction.amount} Credits Reason: {transaction.reason[:100]}'
                    field_value += entry + "\r\n"

            
            embed.add_field(name='Title', value=field_value, inline=True)

            transactions = transactions[5:]

            """

        embed.description = description
        # for transaction in transactions:
        #    embed.add_field(name="Entry", value="", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='leaderboard')
    async def get_leaderboard(self, ctx):
        if ctx.channel.id != 768600365602963496 and ctx.channel.id != 747776646551175217 and ctx.channel.id != 954423559600631832:
            return

        try:
            top_users = self.db.get_top_discord_users(10)
            embed = discord.Embed(title=f"Most Loyal Citizens of D-INFK")
            embed.set_author(name=ctx.author.display_name,
                             icon_url=str(ctx.author.avatar_url))
            embed.set_thumbnail(url=(self.bot.user.avatar_url))

            description = ""
            place = 1
            for user in top_users:
                entry = f'**{place}** **{user.current_name}** with {user.social_credit} Credits'
                description += entry + "\r\n"
                place += 1

            embed.description = description
            # for transaction in transactions:
            #    embed.add_field(name="Entry", value="", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            traceback.print_stack()

    # message listener for 1984 messages
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        db_user = self.db.get_discord_user(message.author.id)

        if db_user is None:
            self.db.create_discord_user(
                message.author.id, message.author.display_name, 1000, message.author.bot, False)

            # User didnt exist in the DB enforce the name
            should_rename = self.bot.db.get_key("ScoreNameChange")
            if should_rename:
                score = f" [1000]"
                new_name = message.author.display_name[:25]+score
                await message.author.edit(nick=new_name)

        # using list comprehension
        # checking if string contains list element
        if [ele for ele in Cog.words_1984 if(ele in message.content.lower())]:
            await self.db.change_credits(message.author, TransactionType.mention_1984, ctx.author.id,
                                         ctx.message.id, ctx.channel.id, None, f"Mentioned word on Blacklist")

    @commands.command(name='add_blacklist')
    @commands.has_permissions(manage_channels=True)
    async def add_blacklist(self, ctx, word):
        Cog.words_1984.add(word)
        await ctx.channel.send(f"'{word.lower()}' added to blacklist")

    @commands.command(name='remove_blacklist')
    @commands.has_permissions(manage_channels=True)
    async def remove_blacklist(self, ctx, word):
        Cog.words_1984.remove(word)
        await ctx.channel.send(f"'{word.lower()}' removed from blacklist")

    @commands.command(name='list_blacklist')
    @commands.has_permissions(manage_channels=True)
    async def list_blacklist(self, ctx):
        await ctx.channel.send(Cog.words_1984)

    @commands.command(name='help')
    async def help_page(self, ctx):
        if ctx.channel.id != 768600365602963496 and ctx.channel.id != 747776646551175217 and ctx.channel.id != 954423559600631832:
            return
        color = discord.Color.green()

        embed = discord.Embed(color=color)
        embed = discord.Embed(title=f"Social Credit Manager Help Page")
        embed.set_author(name=ctx.author.display_name,
                         icon_url=str(ctx.author.avatar_url))
        embed.set_thumbnail(url=(self.bot.user.avatar_url))

        embed.add_field(name="-help", value=f"This command :)", inline=False)
        embed.add_field(name="-transactions <member>",
                        value=f"The last transactions of credits for the provided user. If no users is provided then it shows your credits.", inline=False)
        embed.add_field(
            name="-leaderboard", value=f"Leaderboard of the most loyal citizens. If you are not on it, then you should take an example from them.", inline=False)
        embed.add_field(name="-judge <member> <credits>",
                        value=f"Change the Credits of a User by 20 (Only useable when you have the Judge Icon)", inline=False)
        await ctx.send(embed=embed)

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here


def setup(bot: commands.Bot):
    bot.add_cog(Cog(bot))
