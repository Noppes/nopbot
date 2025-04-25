import discord
from discord.ext import tasks, commands

import requests
import references
import base64
import json
import io

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date, timezone
from bs4 import BeautifulSoup

import lunardate
import convertdate.hebrew as convert_hebrew
import convertdate.gregorian as convert_gregorian

class DaysCog(commands.Cog):
    def __init__(self, bot, logger, cache):
        self.logger = logger
        self.cache = cache
        self.channel = bot.get_channel(references.message_days_channel_id)

        self.lastcheck = False
        self.date_check.start()
    
    def _get_days(self):
        now = datetime.utcnow() - timedelta(hours=10)
        dates = [
            self.chinese_new_year(now.date()),
            self.hanukkah(now.date()),
            self.international_fathersday(now.date()),
            self.international_mothersday(now.date()),
            {
                'date': self._get_date(now, 2, 9),
                'title': 'World Pizza Day 🍕🧑‍🍳',
                'desc': 'A day to celebrate the best food!',
            },
            {
                'date': self._get_date(now, 3, 14),
                'title': 'Pi Day 🥧π',
                'desc': '3.14159265359',
            },
            {
                'date': self._get_date(now, 4, 11),
                'title': 'International Pet Day 🐈🐕',
                'desc': 'Give your pets some extra treats from me!',
            },
            {
                'date': self._get_date(now, 5, 30),
                'title': 'International Potato Day 🥔🥔',
                'desc': 'It\'s International Potato Day today, make sure to say thanks to all your local potatos.',
                'url': 'https://www.fao.org/international-potato-day/en'
            },
            {
                'date': self._get_date(now, 7, 2),
                'title': 'World UFO Day 👽🛸',
                'desc': 'Never stop believing! They are out there!',
            },
            {
                'date': self._get_date(now, 7, 30),
                'title': 'International Day Of Friendship 🫂',
                'desc': 'Tell your besties you love them!',
            },
            {
                'date': self._get_date(now, 8, 8),
                'title': 'International Cat Day 😺',
                'desc': 'Tell your cat I said pspspspsps',
            },
            {
                'date': self._get_date(now, 8, 29),
                'title': 'World Day of Video Games 🎮🕹️',
                'desc': 'The most important celebration of the year!',
            },
            {
                'date': self._get_date(now, 9, 29),
                'title': 'Ask a Stupid Question Day',
                'desc': 'There are no stupid questions! Except for when you ask for mod updates 😑.',
            },
            {
                'date': self._get_date(now, 10, 29),
                'title': 'World Internet Day 🛜🌐',
                'desc': 'Celebrate the most important invention of the last century. Allowing me to meet all you beautiful strangers.',
            },
            {
                'date': self._get_date(now, 11, 2),
                'title': 'Day of the Dead 💀',
                'desc': 'May the souls of your loved ones find peace.',
            },
            {
                'date': self._get_date(now, 12, 25),
                'title': 'Christmas 🎅🎄',
                'desc': 'Merry Christmas everyone!',
            },
            {
                'date': self._get_date(now, 1, 1),
                'title': 'New Year 🎇🎆',
                'desc': 'Happy new year all!',
            }
        ]

        return sorted(dates, key=lambda x: x["date"])

    def _get_date(self, now, month, day):
        d = date(now.year, month, day)
        if d < now.date():
            return date(now.year + 1, month, day)
        return d

    @commands.command()
    async def international_days(self, ctx: commands.context.Context):  
        dates = self._get_days()     
        embed = discord.Embed(
            title="International days"
        )
        formatted_keys = ["**" + date['title'] +":**" for date in dates]        
        formatted_days = [date['date'].strftime('%d-%b-%Y') for date in dates]
        
        embed.add_field(name="", value='\n'.join(formatted_keys), inline=True)
        embed.add_field(name="", value='\n'.join(formatted_days), inline=True)
        self.cache.cache_command_message(ctx.message, await ctx.send(embed=embed))

    @tasks.loop(seconds=60)
    async def date_check(self):
        now = datetime.now(timezone.utc) - timedelta(hours=10)
        if not self.lastcheck or now.day == self.lastcheck.day:
            self.lastcheck = now
            return
        dates = self._get_days()        
        self.lastcheck = now
        for day in dates:
            date = day['date']
            if date.day == now.day and date.month == now.month:
                embed = discord.Embed(
                    title=day['title'],
                    description=day['desc']
                )
                if 'url' in day:
                    embed.url = day['url']
                await self.channel.send(embed=embed) 


    def chinese_new_year(self, now):
        year = now.year        
        date = lunardate.LunarDate(year, 1, 1).toSolarDate()
        if date < now:
            year += 1
            date = lunardate.LunarDate(year, 1, 1).toSolarDate()
            
        animals = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
        animal = animals[(year - 4) % 12]  # Cycle starts at 4 AD with Rat

        return {
                'date': date,
                'title': 'Lunar New Year 🎆🎆',
                'desc': f'Wishing everyone great luck in the Year of the {animal}!'
            }

    def hanukkah(self, now):
        year = now.year
        hebrew_year = convert_hebrew.from_gregorian(year, 12, 1)[0] 
        jd = convert_hebrew.to_jd(hebrew_year, 9, 25)  # 9 = Kislev
        hanukkah_start = date(*convert_gregorian.from_jd(jd))

        if hanukkah_start < now:
            year += 1
            hebrew_year = convert_hebrew.from_gregorian(year, 12, 1)[0] 
            jd = convert_hebrew.to_jd(hebrew_year, 9, 25)  # 9 = Kislev
            hanukkah_start = date(*convert_gregorian.from_jd(jd))

        return {
                'date': hanukkah_start,
                'title': 'Hanukkah 🕎✡️',
                'desc': f'Happy Hanukkah!'
                }

    def international_mothersday(self, now):
        year = now.year
        day = date(year, 5, 1)
        days_until_sunday = (6 - day.weekday()) % 7
        second_sunday = day + timedelta(days=days_until_sunday + 7)

        if second_sunday < now:
            year += 1
            day = date(year, 5, 1)
            days_until_sunday = (6 - day.weekday()) % 7
            second_sunday = day + timedelta(days=days_until_sunday + 7)

        return {
                'date': second_sunday,
                'title': 'International Mothers Day 👩👵',
                'desc': f'Happy International Mothers Day! Give your mother some thanks or I can do it for you tonight 🤖'
                }

    def international_fathersday(self, now):
        year = now.year
        day = date(year, 6, 1)
        days_until_sunday = (6 - day.weekday()) % 7
        third_sunday = day + timedelta(days=days_until_sunday + 14)

        if third_sunday < now:
            year += 1
            day = date(year, 6, 1)
            days_until_sunday = (6 - day.weekday()) % 7
            third_sunday = day + timedelta(days=days_until_sunday + 14)

        return {
                'date': third_sunday,
                'title': 'International Fathers Day 👨👴',
                'desc': f'Happy International Fathers Day! If you still have one, otherwise just give your thanks to me, your daddy 🤖.'
                }

    # def vikram_samvat(self, now):
    #     year = now.year + 57  # Vikram Samvat is 57 years ahead of Gregorian
    #     new_year_date = date(*vs.to_gregorian(year, 1, 1))  # Chaitra Shukla Pratipada

    #     if new_year_date < now:
    #         year += 1
    #         new_year_date = date(*vs.to_gregorian(year, 1, 1))  # Chaitra Shukla Pratipada

    #     return {
    #             'date': new_year_date,
    #             'title': 'Chaitra Shukla Pratipada 🛕🪷',
    #             'desc': f'Wishing everyone a Happy and Prosperous Hindu New Year!!'
    #         }

   