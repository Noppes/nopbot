import discord
import random

responses = [
    "Have you read frequently asked questions?",
    "Noppes has been busy with work, but is still working on this mods",
    "Noppes is still updating to newer version",
    "Updating mods is quite time-consuming, it's still being worked on",
    "Somebody didnt read the rules",
]

async def handle(message: discord.Message):
    msg = message.content.lower().strip()
    if msg.endswith("?") and "update" in msg and ("mod" in msg or "npc" in msg or "mpm" or contains_number(msg)):
        return await message.channel.send(random.choice(responses))
    return False

pattern = r"\d+(\.\d+)+"
def contains_number(string):
    match = re.search(pattern, string)
    return bool(match)