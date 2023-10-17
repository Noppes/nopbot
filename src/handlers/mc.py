import discord
from discord.ext import tasks, commands

import requests
import references
import base64
import json
import io

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class MinecraftCog(commands.Cog):
    def __init__(self, bot, logger, cache):
        self.cache = cache
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

        data = {div.find('h4').get_text(strip=True): div.find('h5').get_text(strip=True)
                for div in java.find_all('div', class_='w3-container')}
        return data

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
            self.cache.cache_command_message(ctx.message, await ctx.send(embed=embed))

    @tasks.loop(seconds=60)
    async def status_check(self):
        result = self.status()
        if not result:
            return
        result.pop("api", None)

        if not self.prev_status:
            self.prev_status = result
            return

        if self.prev_status != result:
            self.count += 1
            was_fine = all(value == "Looks Operational" for value in prev_status.values())
            if(self.count < 6 and was_fine):#making sure the status is changed for multiple minutes
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
        self.cache.cache_command_message(ctx.message, await ctx.send(embed=embed))

    def get_date_diff(self, date1: datetime, date2: datetime):
        age = relativedelta(date2, date1)
        return f"Years: {age.years}, Months: {age.months}, Days: {age.days}"
        

    # https://wiki.vg/Mojang_API
    @commands.command()
    async def mcplayer(self, ctx: commands.context.Context, name:str):        
        response = requests.post(f"https://api.mojang.com/profiles/minecraft", json=[name])

        result = response.json()
        if not result:
            self.cache.cache_command_message(ctx.message, await ctx.send(f"User {name} not found"))
            return
        else:
            response = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/" + result[0]['id'])
            result = response.json()
            embed = discord.Embed(
                title=f"Result for {result['name']}"
            )
            embed.add_field(name="", value="Id: " + result['id'], inline=False)
            embeds = [embed]

            texture_text = next((prop['value'] for prop in result['properties'] if prop["name"] == "textures"), False)
            if texture_text:
                texture = json.loads(base64.b64decode(texture_text).decode('utf-8'))['textures']
                if 'SKIN' in texture:
                    skin_type = "Classic"
                    if 'metadata' in texture['SKIN'] and 'model' in texture['SKIN']['metadata']:
                        skin_type = texture['SKIN']['metadata']['model'].capitalize()
                    embed.add_field(name="", value=f"Skin type: {skin_type}", inline=False)
                    if 'url' in texture['SKIN']:
                        embed.add_field(name="", value=f"Skin url: {texture['SKIN']['url']}", inline=False)
                        embed.set_image(url=texture['SKIN']['url'])
                if 'CAPE' in texture and 'url' in texture['CAPE']:                    
                    cape_embed = discord.Embed(
                        title=f"",
                    )
                    cape_embed.add_field(name="", value=f"Cape url: {texture['CAPE']['url']}", inline=False)
                    cape_embed.set_image(url=texture['CAPE']['url'])
                    embeds.append(cape_embed)

            self.cache.cache_command_message(ctx.message, await ctx.channel.send(embeds=embeds))
                

