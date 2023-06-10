import discord
import random

async def handle(message: discord.Message):
    if message.content.startswith("!roulette"):
        if random.randint(0, 5) == 1:
            return await message.channel.send("Bang!! " + message.author.display_name + " is died")
        else:
            return await message.channel.send("Miss")
    return False