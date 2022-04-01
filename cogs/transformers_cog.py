from discord.ext import commands
from discord.utils import get

from constants import TransactionType
from profanity_check import predict, predict_prob
from transformers import pipeline


class transformerstuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.emotional = pipeline(
            "text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
        self.cutoff = 0.5
        self.switch = 0
        # the fraction of messages we analyze
        self.frac = 10
        self.emotes = {
            0: "anger",
            1: "disgust",
            2: "fear",
            3: "sadness",
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        self.switch += 1
        if self.switch % self.frac == 0:
            self.switch = 0
            prob = predict_prob([message.content])[0]
            if(prob >= self.cutoff):
                await self.db.change_credits(message.author, TransactionType.profanity, message.id, message.channel.id)
                await message.add_reaction("<:badlang:957425440857939978>")
                return
            self.switch += 1
            scores = self.emotional(message.content)
            # At the moment this only looks out for unwanted emotions, we could also reward good emotions if wanted

            relevantscores = [scores[0][0]['score'], scores[0][1]
                              ['score'], scores[0][2]['score'], scores[0][5]['score']]

            for i, score in enumerate(relevantscores):
                if score >= self.cutoff:
                    # TODO: add in that it sends a message about how we don't like the emotion
                    await self.db.change_credits(message.author, TransactionType.emotions, message.id, message.channel.id)
                    await message.add_reaction("<:Illegalemotion:957425440342020197>")


def setup(bot: commands.Bot):
    bot.add_cog(transformerstuff(bot))
