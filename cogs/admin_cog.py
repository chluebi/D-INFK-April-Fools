# library imports
import os
import logging
import traceback
import discord
from discord.ext import commands
from constants import TransactionType

# local imports
import util
import events

from db import SQLiteDBManager
from db import DiscordUser

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db


    @commands.group()
    @commands.has_permissions(manage_channels=True)
    async def admin(self, ctx):
        if ctx.invoked_subcommand is None:
            color = discord.Color.green()

                
            embed = discord.Embed(color=color)
            embed.add_field(name="admin", value=f"this command", inline=False)
            embed.add_field(name="admin loadusers", value=f"Load users into the db", inline=False)
            embed.add_field(name="admin enforcenames", value=f"Enfoce the new style", inline=False)
            embed.add_field(name="admin restorenames", value=f"Restore names to the old style", inline=False)
            embed.add_field(name="admin addkey <key> <value> <type>", value=f"Add Key value pair", inline=False)
            embed.add_field(name="admin getkey <key>", value=f"Get Key value pair", inline=False)
            embed.add_field(name="admin updatekey <key> <value>", value=f"Update Key value pair", inline=False)
            embed.add_field(name="admin allkeys", value=f"Get all key value pairs", inline=False)
            embed.add_field(name="admin sql <query>", value=f"BattleRush's playground", inline=False)
            embed.add_field(name="admin reverttransaction <id>", value=f"Revert transaction Id", inline=False)
            await ctx.send(embed=embed)

    @admin.command(name='loadusers')
    @commands.has_permissions(manage_channels=True)
    async def load_users(self, ctx):
        for member in ctx.guild.members:
            db_user = self.db.get_discord_user(member.id)
        
            if db_user is None:
                #await ctx.channel.send(f"unknown user {member.name} creating")
                #TODO check Name and Nick
                self.db.create_discord_user(member.id, member.name, 1000, member.bot, False)
                
                await ctx.channel.send(f"{member.name} created")

        # enforce naming
    @admin.command(name='enforcenames')
    @commands.has_permissions(manage_channels=True)
    async def enforce_names(self, ctx):
        try:
            for member in ctx.guild.members:
                db_user = self.db.get_discord_user(member.id)

                if db_user is None:
                    #await ctx.channel.send(f"unknown user {member.display_name} creating")
                    #TODO check Name and Nick
                    db_user = self.db.create_discord_user(member.id, member.display_name, 1000, member.bot, False)
                    await ctx.channel.send(f"{member.display_name} created")
                
                credits = str(db_user.social_credit)
                nick = f'{member.display_name[:25]} [{credits}]'
                result = await member.edit(nick=nick)

        except Exception as e:
            print(e)
    
    # restore names
    @admin.command(name='restorenames')
    @commands.has_permissions(manage_channels=True)
    async def restore_names(self, ctx):
        try:
            for member in ctx.guild.members:
                db_user = self.db.get_discord_user(member.id)

                if db_user is None:
                    #await ctx.channel.send(f"unknown user {member.name} creating")
                    #TODO check Name and Nick
                    db_user = self.db.create_discord_user(member.id, member.display_name, 1000, member.bot, False)
                    await ctx.channel.send(f"{member.display_name} created")

                nick = db_user.old_name
                result = await member.edit(nick=nick)

        except Exception as e:
            print(e)

    @admin.command(name='addkey')
    @commands.has_permissions(manage_channels=True)
    async def add_keyvalue(self, ctx, key, value, type):
        returnedValue = self.db.insert_key(key, value, type)
        await ctx.channel.send(key + " set to: " + str(returnedValue))

    @admin.command(name='updatekey')
    @commands.has_permissions(manage_channels=True)
    async def update_keyvalue(self, ctx, key, value):
        returnedValue = self.db.update_key(key, value)
        await ctx.channel.send(key + " set to: " + str(returnedValue))

    @admin.command(name='allkeys')
    @commands.has_permissions(manage_channels=True)
    async def all_keyvalues(self, ctx):
        allKeys = self.db.list_keys()
        await ctx.channel.send(allKeys)

    @admin.command(name='getkey')
    @commands.has_permissions(manage_channels=True)
    async def get_key_value(self, ctx, name):
        value = self.db.get_key(name)
        await ctx.channel.send(value)

    @admin.command(name='sql')
    @commands.has_permissions(manage_channels=True)
    async def sql_query(self, ctx, *, query):
        result = self.db.sql_query(query)
        await ctx.channel.send(result[:2000])    
        
    @admin.command(name='reverttransaction')
    @commands.has_permissions(manage_channels=True)
    async def revert_transaction(self, ctx, id):

        transaction = self.db.get_transaction_by_id(id)
        if transaction is None:
            await ctx.channel.send(f"Transaction with Id: {id} not found")
            return


        #print(transaction)

        member = ctx.guild.get_member(transaction.discord_user_id)
        if member is None:
            await ctx.channel.send(f"Member with Id: {id} not found")
            return
            
        #print(member)

        result = self.db.change_credits(member, TransactionType.revert_transaction, ctx.author.id,
        ctx.message.id, ctx.channel.id, transaction.amount * (-1), f"Reverted transaction {id} with Amount: {transaction.amount}")
        await ctx.channel.send(f"Transaction with Id: {id} was reverted")


def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
