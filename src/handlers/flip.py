import unicodedata
import string
import discord
from discord.ext import tasks, commands

class FlipCog(commands.Cog):
    # Taken from https://github.com/cburgmer/upsidedown

    def __init__(self, bot, logger, cache):
        self.logger = logger
        self.bot = bot
        self.cache = cache
        
        FLIP_RANGES = [
            (string.ascii_lowercase, u"ɐqɔpǝɟƃɥᴉɾʞꞁɯuodbɹsʇnʌʍxʎz"),
            # alternatives: l:ʅ
            (string.ascii_uppercase, u"ⱯᗺƆᗡƎᖵ⅁HIᒋ⋊ꞀWNOԀꝹᴚS⊥∩ɅMX⅄Z"),
            # alternatives: L:ᒣ⅂, J:ſ, F:߃Ⅎ, A:∀ᗄ, U:Ⴖ, W:Ϻ, C:ϽↃ, Q:Ό, M:Ɯꟽ
            (string.digits, u"0ІᘔƐᔭ59Ɫ86"),
            (string.punctuation, u"¡„#$%⅋,)(*+'-˙/:؛>=<¿@]\\[ᵥ‾`}|{~"),
            ]
        UNICODE_COMBINING_DIACRITICS = {'̈': '̤', '̊': '̥', '́': '̗', '̀': '̖',
            '̇': '̣', '̃': '̰', '̄': '̱', '̂': '̬', '̆': '̯', '̌': '̭',
            '̑': '̮', '̍': '̩'}

        self.TRANSLITERATIONS = {'ß': 'ss', u'）':')'}

        self._CHARLOOKUP = {}
        for chars, flipped in FLIP_RANGES:
            self._CHARLOOKUP.update(zip(chars, flipped))

        for char in self._CHARLOOKUP.copy():
            self._CHARLOOKUP[self._CHARLOOKUP[char]] = char

        self._DIACRITICSLOOKUP = dict([(UNICODE_COMBINING_DIACRITICS[char], char)
            for char in UNICODE_COMBINING_DIACRITICS])
        self._DIACRITICSLOOKUP.update(UNICODE_COMBINING_DIACRITICS)

    def transform(self, string):
        for character in self.TRANSLITERATIONS:
            string = string.replace(character, self.TRANSLITERATIONS[character])

        inputChars = list(string)
        inputChars.reverse()

        output = []
        for character in inputChars:
            if character in self._CHARLOOKUP:
                output.append(self._CHARLOOKUP[character])
            else:
                charNormalised = unicodedata.normalize("NFD", character)

                for c in charNormalised[:]:
                    if c in self._CHARLOOKUP:
                        charNormalised = charNormalised.replace(c, self._CHARLOOKUP[c])
                    elif c in self._DIACRITICSLOOKUP:
                        charNormalised = charNormalised.replace(c,
                            self._DIACRITICSLOOKUP[c])

                output.append(unicodedata.normalize("NFC", charNormalised))

        return ''.join(output)

    @commands.command()
    async def flip(self, ctx: commands.context.Context, *, msg:str):
        s = msg.strip()
        if s.lower() == "table":
            self.cache.cache_command_message(ctx.message, await ctx.send(u"(╯°□°)╯︵ ┻━┻"))
        else:
            self.cache.cache_command_message(ctx.message, await ctx.send(u"(╯°□°)╯︵ " + self.transform(s)))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        msg = message.content.lower().strip()
        if u"(╯°□°)╯︵ ┻━┻" in msg:
            self.cache.cache_command_message(message, await message.channel.send(u"(╯°□°)╯︵ " + self.transform(message.author.display_name)))
            return

        if not msg.startswith("flip "):
            return
	
        s = message.content[5:].strip()	
        if not s:
            return False
        if s.lower() == "table":
            self.cache.cache_command_message(message, await message.channel.send(u"(╯°□°)╯︵ ┻━┻"))
        else:
            self.cache.cache_command_message(message, await message.channel.send(u"(╯°□°)╯︵ " + self.transform(s)))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            pass