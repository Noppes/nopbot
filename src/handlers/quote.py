import discord
import requests
from bs4 import BeautifulSoup

async def handle(message: discord.Message):
    if message.content.startswith("!quote"):
        result = quote()
        if result:            
            embed = discord.Embed(
                title="Random Quote",
                description = result["text"],
                url = result["url"]
            )
            embed.set_author(name = result["author"], url = result["author_url"])
            return await message.channel.send(embed=embed) 
    return False

def quote():
    response = requests.get(f"http://www.quotationspage.com/random.php")
    if response.status_code != 200:
        return False
    soup = BeautifulSoup(response.text, 'html.parser')
    quote = soup.find('dt', class_ = "quote")
    author = soup.find('dd', class_ = "author").find("b")
    return {"text": quote.text, "url": "http://www.quotationspage.com" + quote.find("a").get('href'), "author": author.text, "author_url": "http://www.quotationspage.com" + author.find("a").get('href')}

#print(quote())