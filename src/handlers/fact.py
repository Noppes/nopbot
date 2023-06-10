import discord
import requests

async def handle(message: discord.Message):
    if message.content.startswith("!fact"):
        result = fact()
        if result:            
            embed = discord.Embed(
                title="Random Fact",
                description = result["body"],
                url = result["url"]
            )
            if "image" in result:
                embed.set_thumbnail(url = result["image"]["value"]["url"])
            return await message.channel.send(embed=embed) 
    return False

def fact():
    response = requests.get(f"https://facts-service.mmsport.voltaxservices.io/widget/properties/mentalfloss/random-facts?limit=1")
    if response.status_code != 200:
        return False

    return response.json()['data'][0]