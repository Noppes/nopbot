import discord
import util
import references
import signal
import sys
import asyncio
import logging
from normal import shouldi, flip, cat
from commands import anagram, urbandict

intents = discord.Intents.default()
intents.message_content = True

logger = logging.getLogger("nopbot")
logFormatter = logging.Formatter("[%(asctime)s] [%(filename)s(%(lineno)d)] [%(levelname)s] %(message)s",'%y-%m-%d %H:%M:%S')
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.setLevel(logging.INFO)
logger.addHandler(consoleHandler) 

client = discord.Client(intents=intents)
cache = util.CachedMessages()

handlers = [shouldi, flip, cat, urbandict, anagram]

def log_exception(self, exc_type, exc_value, exc_traceback):
    logger.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = log_exception

@client.event
async def on_ready():
    logger.info(f'We have logged in as {client.user}')
    client.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(on_close()))
    await cache.init(client)
    logger.info(f'Finished building cache')

@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    if not (message := payload.cached_message) and not (message := cache.get_cached_message(payload.channel_id, payload.message_id)):
        return

    embed = discord.Embed(
        title = "Message Deleted",
        description = message.content,
        color = discord.Color.red(),
        timestamp = message.created_at
    )
    embed.set_author(name=message.author.name + f" (ID: {message.author.id})", icon_url=message.author.avatar.url, url=message.author.avatar.url)
    embed.timestamp = message.created_at
    if(message.author.id != message.author.id):
        responsible_user = client.get_user(payload.cached_message.author.id)
        if responsible_user:
            embed.add_field(name="Deleted By", value=responsible_user.name)

    await client.get_channel(references.message_channel_id).send(embed=embed)

@client.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent):
    channel = client.get_channel(payload.channel_id)
    after = await channel.fetch_message(payload.message_id)
    before = payload.cached_message or cache.get_cached_message(payload.channel_id, payload.message_id)
    if before and before.content == after.content:
        return
        
    embed = discord.Embed(
        title = "Message Edited",
        color = discord.Color.orange(),
        url = after.jump_url,
        timestamp = after.edited_at
    )
    embed.set_author(name=after.author.name + f" (ID: {after.author.id})", icon_url=after.author.avatar.url, url=after.author.avatar.url)
    if before:
        embed.add_field(name="Before", value=before.content, inline=True)
    else:
        embed.add_field(name="Before", value="N/A", inline=True)
        cache.cache_message(payload.channel_id, after)
    embed.add_field(name="After", value=after.content, inline=True)

    await client.get_channel(references.message_channel_id).send(embed=embed)

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user or message.channel.type != discord.ChannelType.text:
        return
    cache.cache_message(message.channel.id, message)

    for handler in handlers:
        if await handler.handle(message):
            return
    
    #if message.content.startswith('hello'):
    #    await message.channel.send('Hello!')

async def on_close():
    logger.info(f'Stopping bot')
    await client.close()
    sys.exit(0)


client.run(references.token)