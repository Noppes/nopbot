import discord

async def handle(message: discord.Message):
    if message.content.startswith("!version"):
        return await message.channel.send("Using discord.py version " + discord.__version__) 
    return False