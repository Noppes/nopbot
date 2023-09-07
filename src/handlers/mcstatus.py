import discord
from discord.ext import tasks, commands
import requests
import references
from bs4 import BeautifulSoup
import datetime
from datetime import datetime, timedelta

class McStatusCog(commands.Cog):
    def __init__(self, bot, logger):
        self.logger = logger
        self.channel = bot.get_channel(references.message_mcstatus_channel_id)
        self.prev_status = False
        self.count = 0
        self.status_check.start()
        self.date_check.start()

        self.lastcheck = False
        self.mcdate = {
            '1.0.0': datetime(2011, 11, 18),
            '1.2.5': datetime(2012, 4, 4),
            '1.6.4': datetime(2013, 9, 19),
            '1.7.10': datetime(2014, 6, 26),
            '1.8.9': datetime(2015, 12, 9),
            '1.12.2': datetime(2017, 9, 18),
            '1.16.5': datetime(2021, 1, 15),
            '1.18.2': datetime(2022, 2, 28),
        }

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
            embed.add_field(name="", value='\n'.join(formatted_keys), inline=True)
            embed.add_field(name="", value='\n'.join(result.values()), inline=True)
            await self.channel.send(embed=embed) 
    

    @tasks.loop(seconds=60)
    async def date_check(self):
        now = datetime.utcnow() - timedelta(hours=10)
        if not self.lastcheck or now.day == self.lastcheck.day:
            self.lastcheck = now
            return
        self.lastcheck = now
        for key, value in self.mcdate.items():
            if value.day == now.day and value.month == now.month:
                years = now.year - value.year
                embed = discord.Embed(
                    title=f"Minecraft {key}'s birthday 🎂",
                    description=f"Minecraft {key} is now officially {years} years old 🥳🥳"
                )
                await self.channel.send(embed=embed) 


            
    @commands.command()
    async def mcdates(self, ctx: commands.context.Context):
        embed = discord.Embed(
            title="Minecraft Versions"
        )
        now = datetime.utcnow() - timedelta(hours=10)

        formatted_keys = ["**" + key +":**" for key in self.mcdate.keys()]
        formatted_days = [date.strftime('%d-%b-%Y') for date in self.mcdate.values()]
        formatted_ages = [self.get_date_diff(date, now) for date in self.mcdate.values()]

        formatted_keys.insert(0, "**Version:**")
        formatted_days.insert(0, "**Released:**")
        formatted_ages.insert(0, "**Age:**")
        
        embed.add_field(name="", value='\n'.join(formatted_keys), inline=True)
        embed.add_field(name="", value='\n'.join(formatted_days), inline=True)
        embed.add_field(name="", value='\n'.join(formatted_ages), inline=True)
        await ctx.send(embed=embed)

    def get_date_diff(self, date1: datetime, date2: datetime):
        time_difference = date2 - date1

        # Extract years, months, and days from the time difference
        years = time_difference.days // 365
        remaining_days = time_difference.days % 365
        months = remaining_days // 30  # Assuming an average of 30 days per month
        days = remaining_days % 30
        return f"Years: {years}, Months: {months}, Days: {days}"

