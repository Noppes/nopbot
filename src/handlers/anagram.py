import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import tasks, commands

class AnagramCog(commands.Cog):

    def __init__(self, bot, logger):
        self.logger = logger
        self.bot = bot
        
    @commands.command(name="anagram")
    async def anagram_command(self, ctx: commands.context.Context, *, msg:str):
        result = self.anagram(msg)
        if result:
            return await ctx.send(result) 

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            pass

    def anagram(self, msg):
        max_size = int(500 / (len(msg) + 2))
        response = requests.get(f"https://new.wordsmith.org/anagram/anagram.cgi?t={max_size}&anagram=" + msg.replace(" ", "+"))
        if response.status_code != 200:
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        anagram_div = soup.find('blockquote')
        lines = anagram_div.text.strip().split('\n')
        anagrams = []
        start = False
        for line in lines:
            if start:
                if not line:
                    break
                anagrams.append(line)
            if "Displaying" in line:
                start = True
            if "No anagrams found." in line:
                return "No anagram found"
                break
        return ", ".join(anagram.strip() for anagram in anagrams[:max_size])