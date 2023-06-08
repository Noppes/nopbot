import discord
import random

async def handle(message: discord.Message):
    if message.content.startswith("!choose "):
        arr = message.content[8:].strip().split(" or ")

        if len(arr) >= 2:
            await message.channel.send(random.choice(arr)) 