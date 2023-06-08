import discord
from random import randint
keywords = ("should ", "will ", "do ", "am i ", "does ", "are ", "did ", "is ")

async def handle(message: discord.Message):
    msg = message.content.lower().strip()
    if msg.endswith("?") and msg.startswith(keywords):
        i = randint(0, 5)
        if i == 0:
            await message.channel.send("Yes")
        elif i == 1:
            await message.channel.send("No")
        elif i == 2:
            await message.channel.send("Probably")
        elif i == 3:
            await message.channel.send("Probably not")
        elif i == 4:
            await message.channel.send("Definitely")
        elif i == 5:
            await message.channel.send("Definitely not")
        return True
    return False
