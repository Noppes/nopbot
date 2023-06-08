import unicodedata
import string
import re
import discord

# Taken from https://github.com/cburgmer/upsidedown
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

TRANSLITERATIONS = {'ß': 'ss', u'）':')'}

_CHARLOOKUP = {}
for chars, flipped in FLIP_RANGES:
    _CHARLOOKUP.update(zip(chars, flipped))

for char in _CHARLOOKUP.copy():
    _CHARLOOKUP[_CHARLOOKUP[char]] = char

_DIACRITICSLOOKUP = dict([(UNICODE_COMBINING_DIACRITICS[char], char)
    for char in UNICODE_COMBINING_DIACRITICS])
_DIACRITICSLOOKUP.update(UNICODE_COMBINING_DIACRITICS)

def transform(string):
    for character in TRANSLITERATIONS:
        string = string.replace(character, TRANSLITERATIONS[character])

    inputChars = list(string)
    inputChars.reverse()

    output = []
    for character in inputChars:
        if character in _CHARLOOKUP:
            output.append(_CHARLOOKUP[character])
        else:
            charNormalised = unicodedata.normalize("NFD", character)

            for c in charNormalised[:]:
                if c in _CHARLOOKUP:
                    charNormalised = charNormalised.replace(c, _CHARLOOKUP[c])
                elif c in _DIACRITICSLOOKUP:
                    charNormalised = charNormalised.replace(c,
                        _DIACRITICSLOOKUP[c])

            output.append(unicodedata.normalize("NFC", charNormalised))

    return ''.join(output)

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

async def handle(message: discord.Message):
    if message.content == u"(╯°□°)╯︵ ┻━┻":
        await message.channel.send(u"(╯°□°)╯︵ " + transform(message.author.name))        
        return
        
    msg = message.content.lower().strip()
    if not msg.startswith("flip "):
        return
	
    s = message.content[5:].strip()	
    if not s:
        return
    if s.lower() == "table":
        await message.channel.send(u"(╯°□°)╯︵ ┻━┻")
    else:
        await message.channel.send(u"(╯°□°)╯︵ " + transform(s))