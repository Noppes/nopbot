import discord
from discord.ext import tasks, commands
import random
import re

class QuestionCog(commands.Cog):

    def __init__(self, bot, logger, cache):
        self.logger = logger
        self.bot = bot
        self.cache = cache
        self.keywords = ("should ", "will ", "do ", "am i ", "does ", "are ", "did ", "is ", "that ", "were ", "does ", "was ")
        self.responses = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes - definitely",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "No",
            "Signs point to yes",
            "Ask again later",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful"
        ]
        self.version_pattern = r"\d+(\.\d+)+"
        self.update_responses = [
            "Have you read frequently asked questions?",
            "Noppes has been busy with work, but is still working on this mods",
            "Noppes is still updating to newer version",
            "Updating mods is quite time-consuming, it's still being worked on",
            "Somebody didnt read the rules",
        ]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        msg = message.content.lower().strip()

        if msg.endswith("?") and "update" in msg and ("mod" in msg or "npc" in msg or "mpm" or self.contains_number(msg)):
            self.cache.cache_command_message(message, await message.channel.send(random.choice(self.update_responses)))

        elif msg.endswith("?") and msg.startswith(self.keywords):
            self.cache.cache_command_message(message, await message.channel.send(random.choice(self.responses)))
        
        
    def contains_number(self, string):
        return bool(re.search(self.version_pattern, string))
