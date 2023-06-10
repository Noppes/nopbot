import discord
import random

async def handle(message: discord.Message):
    if message.content.startswith("!roll"):
        msg = message.content[5:].strip()
        number = 6
        if len(msg) > 0:
            try:
                number = int(msg)
            except ValueError:
                return await message.channel.send(msg + " is not an number")
        if number <= 1:
            return await message.channel.send("You can't roll a number lower than 1")
        
        return await message.channel.send(message.author.display_name + " rolled " + str(random.randint(1, number)))

    return False