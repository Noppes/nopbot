import discord
from discord.ext import tasks, commands
import requests
import references
from bs4 import BeautifulSoup

class McStatusCog(commands.Cog):
    def __init__(self, bot, logger):
        self.logger = logger
        self.channel = bot.get_channel(references.message_mcstatus_channel_id)
        self.prev_status = False
        self.count = 0
        self.status_check.start()

    def status(self):
        response = requests.get("https://minecraftstatus.net/")
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        java = soup.find('h3', text = "Minecraft Java").find_parent()
        divs = java.find_all('div', class_='w3-container')

        return {div.find('h4').get_text(strip=True): div.find('h5').get_text(strip=True)
                for div in java.find_all('div', class_='w3-container')}

    @commands.command()
    async def mcstatus(self, ctx: commands.context.Context):
        result = self.status()
        if result:            
            embed = discord.Embed(
                title="Minecraft Status",
                url = "https://minecraftstatus.net/"
            )
            formatted_keys = ["**" + key +":**" for key in result.keys()]
            
            embed.add_field(name="", value='\n'.join(formatted_keys), inline=True)
            embed.add_field(name="", value='\n'.join(result.values()), inline=True)
            await ctx.send(embed=embed)

    @tasks.loop(seconds=60)
    async def status_check(self):
        result = self.status()
        if not result:
            return
        api_value = result.pop('api')

        if not self.prev_status:
            self.prev_status = result
            return

        if self.prev_status != result:
            self.count += 1
            if(self.count < 6):#making sure the status is changed for multiple minutes
                return
            self.count = 0
            self.prev_status = result
            description = "Minecraft services no longer have issues" if all(value == "Looks Operational" for value in result.values()) else "Looks like one of Minecraft's services is experiencing issues"
            embed = discord.Embed(
                title="Minecraft Status",
                url = "https://minecraftstatus.net/",
                description=description
            )
            formatted_keys = ["**" + key +":**" for key in result.keys()]
            formatted_keys.append("**api:**")
            embed.add_field(name="", value='\n'.join(formatted_keys), inline=True)
            embed.add_field(name="", value='\n'.join(result.values()) + '\n' + api_value, inline=True)
            await self.channel.send(embed=embed) 

