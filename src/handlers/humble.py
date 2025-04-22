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

class HumbleCog(commands.Cog):
    def __init__(self, bot, logger, cache):
        self.cache = cache
        self.logger = logger
        self.channel = bot.get_channel(references.message_gaming_channel_id)
        self.bundle_types = ['games', 'books', 'software']
        self.availble_bundles = []
        self.bundles_check.start()
        
        self.availble_epicgames = []
        self.epicgames_check.start()

    @commands.command()
    async def bundles(self, ctx: commands.context.Context, bundle_type:str = "games"):
        if bundle_type not in self.bundle_types:
            bundle_type = "games"

        bundles = self.get_bundles()
        if bundle_type not in bundles:
            await ctx.channel.send(f"No bundles currently available for `{bundle_type}`")
            return True
        products = bundles[bundle_type]
        embeds = []
        for prod in products:
            embeds.append(self.product_embed(prod))
        for i in range(0, len(embeds), 10):
            await ctx.channel.send(embeds=embeds[i:i + 10]) 
    
    def format_blurb(self, text:str):
        text = text.replace('<em>', '**')
        text = text.replace('</em>', '**')
        text = text.replace('<br>', '\n')
        return text

    def product_embed(self, prod) -> discord.Embed:
        embed = discord.Embed(
            title=prod['tile_name'],
            description=self.format_blurb(prod['marketing_blurb']),
            url="https://www.humblebundle.com" + prod['product_url']
        )
        embed.set_image(url=prod['tile_image'])
        start_date = datetime.strptime(prod['start_date|datetime'], "%Y-%m-%dT%H:%M:%S")
        end_date = datetime.strptime(prod['end_date|datetime'], "%Y-%m-%dT%H:%M:%S")
        embed.add_field(name="Start Date", value=start_date.strftime("%d-%b-%Y"))
        embed.add_field(name="End Date", value=end_date.strftime("%d-%b-%Y"))
        difference = end_date - datetime.utcnow()
        if difference.days > 1:
            embed.add_field(name="Countdown", value=f"{difference.days} Days left ")
        else:
            total_seconds = difference.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            embed.add_field(name="Countdown", value=f"{hours:02}:{minutes:02}:{seconds:02}")
        return embed

    def get_bundles(self):
        result = {}
        response = requests.get("https://www.humblebundle.com/bundles")
        if response.status_code != 200:
            return result
        soup = BeautifulSoup(response.text, 'html.parser')
        bundles_data = soup.find('script', id="landingPage-json-data").get_text()
        bundles = json.loads(bundles_data)['data']

        for bundle_type in self.bundle_types:
            if bundle_type in bundles and len(bundles[bundle_type]['mosaic']) > 0:
                result[bundle_type] = bundles[bundle_type]['mosaic'][0]['products']
        return result

    def get_names(self, bundles):
        result = []
        for bundle_type in self.bundle_types:
            if bundle_type in bundles:
                result.extend([item['product_url'] for item in bundles[bundle_type]])
        return result


    @commands.command()
    async def epicgames(self, ctx: commands.context.Context):
        games = self.get_epicgames()
        if not games:
            await ctx.channel.send(f"No free epic games found")
            return True
        embeds = []
        for game in games:
            embeds.append(self.epicgames_embed(game))
        for i in range(0, len(embeds), 10):
            await ctx.channel.send(embeds=embeds[i:i + 10]) 

    @tasks.loop(hours=12)
    async def bundles_check(self):
        bundles = self.get_bundles()
        machine_names = self.get_names(bundles)
        if len(bundles) == 0 or len(machine_names) == 0:
            return
        new_names = [item for item in machine_names if item not in self.availble_bundles]
        if len(self.availble_bundles) > 0 and len(new_names) > 0:
            embeds = []
            for bundle_type, products in bundles.items():
                for prod in products:
                    if prod['product_url'] in new_names:
                        embed = self.product_embed(prod)
                        embed.add_field(name="Category", value=bundle_type.capitalize(), inline=False)
                        embeds.append(embed)
            if len(embeds) > 0:
                message = f"{len(embeds)} new Humble Bundles:"
                for i in range(0, len(embeds), 10):
                    await self.channel.send(content=message, embeds=embeds[i:i + 10]) 
                    message = None

        self.availble_bundles = machine_names

    
    @tasks.loop(hours=12)
    async def epicgames_check(self): # https://store.epicgames.com/en-US/free-games
        games = self.get_epicgames()
        machine_names = list({d["id"] for d in games})
        if len(games) == 0 or len(machine_names) == 0:
            return
        new_names = [item for item in machine_names if item not in self.availble_epicgames]
        if len(self.availble_epicgames) > 0 and len(new_names) > 0:
            embeds = []
            for prod in games:
                if prod['id'] in new_names:
                    embed = self.epicgames_embed(prod)
                    embed.add_field(name="Category", value="Epic Games Store", inline=False)
                    embeds.append(embed)
            if len(embeds) > 0:
                message = f"{len(embeds)} new Epic Store free game:"
                for i in range(0, len(embeds), 10):
                    await self.channel.send(content=message, embeds=embeds[i:i + 10]) 
                    message = None

        self.availble_epicgames = machine_names

        

    def get_epicgames(self):
        response = requests.get("https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US")
        if response.status_code != 200:
            return []
        games = json.loads(response.text)['data']['Catalog']['searchStore']['elements']

        result = []
        for game in games:
            if game['offerMappings'] and game['promotions'] and game['promotions']['promotionalOffers']:
                result.append(game)
        return result

    def epicgames_embed(self, game) -> discord.Embed:
        try:
            embed = discord.Embed(
                title=game['title'],
                description=self.format_blurb(game['description']),
                url="https://store.epicgames.com/en-US/p/" + game['offerMappings'][0]['pageSlug']
            )
            embed.set_image(url=game['keyImages'][0]['url'])
            start_date = datetime.strptime(game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['startDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
            end_date = datetime.strptime(game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
            embed.add_field(name="Start Date", value=start_date.strftime("%d-%b-%Y"))
            embed.add_field(name="End Date", value=end_date.strftime("%d-%b-%Y"))
            difference = end_date - datetime.utcnow()
            if difference.days > 1:
                embed.add_field(name="Countdown", value=f"{difference.days} Days left ")
            else:
                total_seconds = difference.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                embed.add_field(name="Countdown", value=f"{hours:02}:{minutes:02}:{seconds:02}")
            return embed
        except Exception as e:
            self.logger.exception(e)
            self.logger.info(game)
