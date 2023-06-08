import discord
import requests

async def handle(message: discord.Message):
    if message.content == "show me a cat":
        response = requests.get("http://thecatapi.com/api/images/get?format=src&type=gif")
        if response.status_code == 200:
            await message.channel.send(response.url) 