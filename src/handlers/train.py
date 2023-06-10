import discord
import random
import references

async def handle(message: discord.Message):
    if message.content.startswith("!train"):
        return await message.channel.send("All aboard!! CHOO" + ('O' * random.randint(0, 12)) + " CHOOOO"  + ('O' * random.randint(0, 24))) 
    return False