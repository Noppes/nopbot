import discord
import requests
import random
from discord.ext import tasks, commands

class SimpleCommandsCog(commands.Cog):

    def __init__(self, bot, logger, cache):
        self.logger = logger
        self.bot = bot
        self.cache = cache

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            return
        if isinstance(error, commands.errors.BadArgument):
            return
        raise error


    @commands.command()
    async def cat(self, ctx: commands.context.Context):
        response = requests.get("http://thecatapi.com/api/images/get?format=src&type=gif")
        if response.status_code == 200:
            await self.send(ctx, response.url) 

    @commands.command()
    async def dog(self, ctx: commands.context.Context):
        response = requests.get("http://thedogapi.com/api/images/get?format=src&type=gif")
        if response.status_code == 200:
            await self.send(ctx, response.url) 

    @commands.command()
    async def train(self, ctx: commands.context.Context):
        await self.send(ctx, "All aboard!! CHOO" + ('O' * random.randint(0, 12)) + " CHOOOO"  + ('O' * random.randint(0, 24))) 

    @commands.command()
    async def version(self, ctx: commands.context.Context):
        await self.send(ctx, "Using discord.py version " + discord.__version__)  

    @commands.command(aliases=["rr"])
    async def russianroulette(self, ctx: commands.context.Context):
        if random.randint(0, 5) == 1:
            await self.send(ctx, f"Bang!! {ctx.author.display_name} is dead")
        else:
            await self.send(ctx, "Miss")

    @commands.command()
    async def roll(self, ctx: commands.context.Context, number:int = 6):
        if number <= 1:
            return await ctx.send("You can't roll a number lower than 1")
        await self.send(ctx, ctx.author.display_name + " rolled " + str(random.randint(1, number)))

    @commands.command()
    async def choose(self, ctx: commands.context.Context, *, msg:str):
        arr = msg.strip().split(" or ")
        if len(arr) >= 2:
            await self.send(ctx, random.choice(arr)) 

    @commands.command(name="commands")
    async def commands_(self, ctx: commands.context.Context):
        command_names = [command.name for command in self.bot.commands]
        await self.send(ctx, "Available commands: " + ', '.join(command_names)) 

    @commands.command()
    async def lenny(self, ctx: commands.context.Context):
        mouth = random.choice([["v"],["ᴥ"],["ᗝ"],["Ѡ"],["ᗜ"],["Ꮂ"],["ᨓ"],["ᨎ"],["ヮ ]"],["╭͜ʖ╮"],[" ͟ل͜"],[" ͜ʖ"],[" ͟ʖ"],[" ʖ̯"],["ω"],[" ³"],[" ε "],["﹏"],["□"],["ل͜"],["‿"],["╭╮"],["‿‿"],["▾"],["‸"],["Д"],["∀"],["!"],["人"],["."],["ロ"],["_"],["෴"],["ꔢ"],["ѽ"],["ഌ"],["⏠"],["⏏"],["⍊"],["⍘"],["ツ"],["益"]])
        eyes = random.choice([["⌐■","■"],[" ͠°"," °"],["⇀","↼"],["´• "," •`"],["´","`"],["`","´"],["ó","ò"],["ò","ó"],["⸌","⸍"],[u"\u003e",u"\u003c"],["Ɛ","3"],["ᗒ","ᗕ"],["⟃","⟄"],["⪧","⪦"],["⪦","⪧"],["⪩","⪨"],["⪨","⪩"],["⪰","⪯"],["⫑","⫒"],["⨴","⨵"],["⩿","⪀"],["⩾","⩽"],["⩺","⩹"],["⩹","⩺"],["◥▶","◀◤"],["≋"],["૦ઁ"],["  ͯ"],["  ̿"],["  ͌"],["ꗞ"],["ꔸ"],["꘠"],["ꖘ"],["܍"],["ළ"],["◉"],["☉"],["・"],["▰"],["ᵔ"],[" ﾟ"],["□"],["☼"],["*"],["`"],["⚆"],["⊜"],[u"\u003e"],["❍"],["￣"],["─"],["✿"],["•"],["T"],["^"],["ⱺ"],["@"],["ȍ"],["  "],["  "],["x"],["-"],["$"],["Ȍ"],["ʘ"],["Ꝋ"],[""],[""],["⸟"],["๏"],["ⴲ"],["■"],[" ﾟ"],["◕"],["◔"],["✧"],["■"],["♥"],[" ͡°"],["¬"],[" º "],["⨶"],["⨱"],["⏓"],["⏒"],["⍜"],["⍤"],["ᚖ"],["ᴗ"],["ಠ"],["σ"]])
        ears = random.choice([["q","p"],["ʢ","ʡ"],["⸮","?"],["ʕ","ʔ"],["ᖗ","ᖘ"],["ᕦ","ᕥ"],["ᕦ(",")ᕥ"],["ᕙ(",")ᕗ"],["ᘳ","ᘰ"],["ᕮ","ᕭ"],["ᕳ","ᕲ"],["(",")"],["[","]"],[r'¯\\_','_/¯'],["୧","୨"],["୨","୧"],["⤜(",")⤏"],["☞","☞"],["ᑫ","ᑷ"],["ᑴ","ᑷ"],["ヽ(",")ﾉ"],[r'\\(',')/'],["乁(",")ㄏ"],["└[","]┘"],["(づ",")づ"],["(ง",")ง"],["|"]])
        
        await self.send(ctx, ears[0] + " " + eyes[0] + " " + mouth[0] + " " + eyes[len(eyes) - 1] + " " + ears[len(ears) - 1])

    async def send(self, ctx: commands.context.Context, msg: str):
        self.cache.cache_command_message(ctx.message, await ctx.send(msg))