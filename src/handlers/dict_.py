import discord
from discord.ext import tasks, commands
import requests
import jellyfish
import random
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote

class DictCog(commands.Cog):

    def __init__(self, bot, logger):
        self.logger = logger
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            pass

    @commands.command(name="dict")
    async def dict_command(self, ctx: commands.context.Context, *, msg:str):
        result = self.dict_(msg)
        if not result or not result["descriptions"]:
            return await ctx.send("No results found for: " + msg) 

        embed = discord.Embed(
            title = "Dictionary: " + msg.capitalize(),
            url = f"https://glosbe.com/en/en/{quote(msg)}"
        )
        embed.add_field(name="Definitions",  value="\n".join(["- " + item for item in result["descriptions"]]), inline=False)
        embed.add_field(name="Examples",     value="\n".join(["- " + item for item in result["examples"]]), inline=False)
        await ctx.send(embed=embed) 

    def longest_common_substring(self, string1, string2):
        m = len(string1)
        n = len(string2)

        lengths = [[0] * (n + 1) for _ in range(m + 1)]

        max_length = 0
        end_pos = 0

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if string1[i - 1] == string2[j - 1]:
                    lengths[i][j] = lengths[i - 1][j - 1] + 1
                    if lengths[i][j] > max_length:
                        max_length = lengths[i][j]
                        end_pos = i

        longest_substring = string1[end_pos - max_length: end_pos]

        return longest_substring

    def similar_strings(self, s1, s2):
        if s1 == s2:
            return True
        if not s1 or not s2:
            return False
        if (1 - (jellyfish.levenshtein_distance(s1, s2) / max(len(s1), len(s2)))) > 0.8:
            return True
        if jellyfish.jaro_distance(s1, s2) > 0.8:
            return True
        lcs = self.longest_common_substring(s1, s2)
        if len(lcs) / len(s1) > 0.8:
            return True
        return False

    def dict_(self, msg):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(f"https://glosbe.com/en/en/{quote(msg)}", headers=headers)
        if response.status_code != 200:
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find('ul', class_ = "list-disc text-sm dir-aware-pl-6")
        sorted_list = sorted(elements, key=lambda x: len(x), reverse=True)
        definitions = []
        for li in sorted_list:
            s = li.get_text().replace('\n', ' ').strip()
            if not s:
                continue
            add = True
            for d in definitions:
                if self.similar_strings(s, d):
                    add = False
                    break
            if add:
                definitions.append(s)
        elements = soup.find('div', id = "tmem_first_examples").find_all('span')
        examples = [li.get_text() for li in elements if li.get_text() and len(li.get_text()) <= 200]

        num_examples = max(7 - len(definitions), 3)    
        return {'descriptions': definitions[:4], 'examples': random.sample(examples, num_examples)}
        
    @commands.command(name="urbandict")
    async def urbandict_command(self, ctx: commands.context.Context, *, msg:str = None):
        result = self.urbandict(msg)
        if result:
            embed = discord.Embed(
                title = "Urban Dictionary: " + result['word'].capitalize(),
                timestamp = datetime.strptime(result['written_on'], "%Y-%m-%dT%H:%M:%S.%fZ") ,
                url = result['permalink']
            )
            embed.add_field(name="Definition",  value=result['definition'].replace("[", "").replace("]", ""), inline=False)
            embed.add_field(name="Example",     value=result['example'].replace("[", "").replace("]", ""), inline=False)
            return await ctx.send(embed=embed) 
        result = self.urbandict_autocomplete(msg)
        return await ctx.send(f"Could not find any results, did you perhaps mean: {result}" if result else f"No results found for {msg}") 

    def urbandict_autocomplete(self, msg = None):
        response = requests.get(f"https://api.urbandictionary.com/v0/autocomplete?term={quote(msg)}")
        if response.status_code != 200:
            return False
        return ", ".join(response.json())

    def urbandict(self, msg = None):
        if not msg:
            url = "https://api.urbandictionary.com/v0/random"
        else:
            url = f"https://api.urbandictionary.com/v0/define?term={quote(msg)}"

        response = requests.get(url)
        if response.status_code != 200:
            return False

        result = response.json()
        sorted_list = sorted(result["list"], key=lambda x: (self.similar_strings(msg, x["word"]), x["thumbs_up"]), reverse=True)
        return sorted_list[0] if sorted_list else None

#print(dict("your mom"))