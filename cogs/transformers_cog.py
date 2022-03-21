import asyncio

import discord
import events
from discord.ext import commands
from db import SQLiteDBManager

from bot import discord_config

from constants import TransactionType

from transformers import pipeline

class transformerstuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.emotional = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
        self.cutoff = 0.5
        self.switch = 0
        #the fraction of messages we analyze
        self.frac = 2
        self.emotes = {
            0 : "anger",
            1 : "disgust",
            2 : "fear",
            3 : "sadness",
        }
    
    @commands.Cog.listener()
    async def on_message(self, message):
        self.switch += 1
        if self.switch == self.frac or len(message.content) >= 500:
            self.switch = 0
            return
        scores = self.emotional(message.content)
        # At the moment this only looks out for unwanted emotions, we could also reward good emotions if wanted

        relevantscores = [scores[0][0]['score'], scores[0][1]['score'], scores[0][2]['score'], scores[0][5]['score']]
        disgustprob = scores[0][1]['score']
        fearprob = scores[0][2]['score']
        sadprob = scores[0][5]['score']

        for i, score in enumerate(relevantscores):
            if score >= self.cutoff:
                print("I dont like that you are: ",self.emotes[i])
                #TODO: add in that it sends a message about how we don't like the emotion
                self.db.change_credits(message.author, TransactionType.emotions, message.id, message.channel.id)



def setup(bot: commands.Bot):
    bot.add_cog(transformerstuff(bot))