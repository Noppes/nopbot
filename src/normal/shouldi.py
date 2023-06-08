import discord
import random

keywords = ("should ", "will ", "do ", "am i ", "does ", "are ", "did ", "is ", "that")
responses = [
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

async def handle(message: discord.Message):
    msg = message.content.lower().strip()
    if msg.endswith("?") and msg.startswith(keywords):
        await message.reply(random.choice(responses))
        return True
    return False
