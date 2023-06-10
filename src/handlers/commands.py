import discord

async def handle(message: discord.Message):
    if message.content.startswith("!commands"):
        return await message.channel.send("Available commands: !anagram, !cat, !choose, !dict, !urbandict, !fact, !flip, !lenny, !meme, !quote, !roll, !russianroulette, !train")
    return False