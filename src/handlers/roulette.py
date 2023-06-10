import discord
import random

async def handle(message: discord.Message):
    if message.content.startswith("!russianroulette") or message.content.startswith("!rr"):
        if random.randint(0, 5) == 1:
            return await message.channel.send(f"Bang!! {message.author.display_name} is dead")
        else:
            return await message.channel.send("Miss")
    return False