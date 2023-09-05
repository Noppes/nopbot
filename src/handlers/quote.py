import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import tasks, commands

class QuoteCog(commands.Cog):

    def __init__(self, bot, logger):
        self.logger = logger
        self.bot = bot

    @commands.command()
    async def quote(self, ctx: commands.context.Context):
        response = requests.get(f"http://www.quotationspage.com/random.php")
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        quote = soup.find('dt', class_ = "quote")
        author = soup.find('dd', class_ = "author").find("b")
         
        embed = discord.Embed(
            title="Random Quote",
            description = quote.text,
            url = "http://www.quotationspage.com" + quote.find("a").get('href')
        )
        embed.set_author(name = author.text, url = "http://www.quotationspage.com" + author.find("a").get('href'))
        return await ctx.send(embed=embed) 

    @commands.command()
    async def fact(self, ctx: commands.context.Context):
        response = requests.get(f"https://facts-service.mmsport.voltaxservices.io/widget/properties/mentalfloss/random-facts?limit=1")
        if response.status_code != 200:
            return

        result = response.json()['data'][0]
        if not result:
            return
        embed = discord.Embed(
            title="Random Fact",
            description = result["body"],
            url = result["url"]
        )
        if "image" in result:
            embed.set_thumbnail(url = result["image"]["value"]["url"])
        await ctx.send(embed=embed) 
#print(quote())