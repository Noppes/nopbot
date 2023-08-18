import discord
import requests
from datetime import datetime
from urllib.parse import quote

async def handle(message: discord.Message):
    if message.content.startswith("!urbandict"):
        msg = message.content[10:].strip()
        result = urbandict(msg)
        if result:
            embed = discord.Embed(
                title = "Urban Dictionary: " + result['word'].capitalize(),
                timestamp = datetime.strptime(result['written_on'], "%Y-%m-%dT%H:%M:%S.%fZ") ,
                url = result['permalink']
            )
            embed.add_field(name="Definition",  value=result['definition'].replace("[", "").replace("]", ""), inline=False)
            embed.add_field(name="Example",     value=result['example'].replace("[", "").replace("]", ""), inline=False)
            return await message.channel.send(embed=embed) 
        result = urbandict_autocomplete(msg)
        return await message.channel.send(f"Could not find any results, did you perhaps mean: {result}" if result else f"No results found for {msg}") 
        
    return False

def urbandict_autocomplete(msg = None):
    response = requests.get(f"https://api.urbandictionary.com/v0/autocomplete?term={quote(msg)}")
    if response.status_code != 200:
        return False
    return ", ".join(response.json())

def urbandict(msg = None):
    if not msg:
        url = "https://api.urbandictionary.com/v0/random"
    else:
        url = f"https://api.urbandictionary.com/v0/define?term={quote(msg)}"

    response = requests.get(url)
    if response.status_code != 200:
        return False

    result = response.json()
    sorted_list = sorted(result["list"], key=lambda x: x["thumbs_up"], reverse=True)
    return sorted_list[0] if sorted_list else None

#print(urbandict())