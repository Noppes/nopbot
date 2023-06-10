import discord
import requests

keywords = ["show me a cat", "!cat", "i need a cat"]

async def handle(message: discord.Message):
    if message.content.lower() in keywords:
        response = requests.get("http://thecatapi.com/api/images/get?format=src&type=gif")
        if response.status_code == 200:
            return await message.channel.send(response.url) 
    return False