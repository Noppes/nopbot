import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup

class MemeCog(commands.Cog):

    def __init__(self, bot, logger):
        self.logger = logger
        self.bot = bot
        
    @commands.command(name="meme")
    async def meme_command(self, ctx: commands.context.Context):
        response = await ctx.send("Retrieving meme")
        result = self.meme()
        if result:            
            embed = discord.Embed(
                title=result["title"],
                description = result["text"],
                url = result["url"]
            )
            if "image" in result:
                embed.set_thumbnail(url = result["image"])
            if "Year" in result:
                embed.add_field(name="Year", value=result["Year"], inline=True)
            if "Type" in result:
                embed.add_field(name="Type", value=result["Type"], inline=True)
            if "Origin" in result:
                embed.add_field(name="Origin", value=result["Origin"], inline=True)
            if "Status" in result:
                embed.add_field(name="Status", value=result["Status"], inline=True)
            await response.edit(content = "", embed=embed)
        else:
            await response.edit(content = "Failed getting a meme")
        return response

    def meme(self, tries = 0):
        if tries > 8:
            return False
        response = requests.get(f"https://knowyourmeme.com/random")
        if response.status_code != 200:
            return False

        soup = BeautifulSoup(response.text, 'html.parser')

        div_element = soup.find('div', class_='c', id='entry_body')
        data_dict = {dt.get_text(strip=True): dt.find_next('dd').get_text(strip=True)
                for dt in div_element.find_all('dt')}
        
        if (tries <= 2 and data_dict["Status"] != "Confirmed") or (tries > 2 and data_dict["Status"] == "Deadpool"):
            return self.meme(tries = tries + 1)
        
        data_dict['url'] = response.url
        data_dict['text'] = soup.find('meta', attrs={'property': 'og:description', 'content': True})["content"]
        data_dict['title'] = soup.find('meta', attrs={'property': 'og:title', 'content': True})["content"]
        if image := soup.find('link', attrs={'as': 'image', 'href': True}):
            data_dict['image'] = image["href"]

        return data_dict

#print(meme())