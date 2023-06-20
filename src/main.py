import discord
import util
import references
import signal
import sys
import asyncio
import logging
from collections import deque
from handlers import shouldi, flip, cat, dog, anagram, urbandict, choose, dict_, faces, fact, quote, roulette, meme, train, commands, lenny, roll, version, update_question

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
command_cache = deque(maxlen=500)

handlers = [update_question, shouldi, flip, cat, dog, urbandict, anagram, choose, dict_, faces, fact, meme, quote, roulette, train, commands, lenny, roll, version]

def log_exception(self, exc_type, exc_value, exc_traceback):
    logger.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = log_exception

@client.event
async def on_ready():
    logger.info(f'Discord.py {discord.__version__}')
    logger.info(f'We have logged in as {client.user}')
    client.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(on_close()))
    await cache.init(client)
    logger.info(f'Finished building cache')

@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    response = next((item['response'] for item in command_cache if item['message_id'] == payload.message_id), None)
    if response:
        try:
            await response.delete()
        except:
            pass

    if not (message := payload.cached_message) and not (message := cache.get_cached_message(payload.channel_id, payload.message_id)):
        return

    embed = discord.Embed(
        title = "Message Deleted from #" + client.get_channel(payload.channel_id).name ,
        description = message.content,
        color = discord.Color.red(),
        timestamp = message.created_at
    )
    embed.set_author(name=message.author.display_name + f" (ID: {message.author.id})", icon_url=message.author.avatar.url, url=message.author.avatar.url)
    if message.attachments:
        embed.add_field(name="Attachements",  value="\n".join(["- " + item.url for item in message.attachments]), inline=False)


    embed.timestamp = message.created_at
    if message.author.id != message.author.id:
        responsible_user = client.get_user(payload.cached_message.author.id)
        if responsible_user:
            embed.add_field(name="Deleted By", value=responsible_user.name)

    await client.get_channel(references.message_channel_id).send(embed=embed)

@client.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent):
    channel = client.get_channel(payload.channel_id)
    after = await channel.fetch_message(payload.message_id)
    if after.author.id == client.user.id:
        return
    before = payload.cached_message or cache.get_cached_message(payload.channel_id, payload.message_id)
    if before and before.content == after.content:
        return
        
    embed = discord.Embed(
        title = "Message Edited",
        color = discord.Color.orange(),
        url = after.jump_url,
        timestamp = after.edited_at
    )
    embed.set_author(name=after.author.display_name + f" (ID: {after.author.id})", icon_url=after.author.avatar.url, url=after.author.avatar.url)
    if before:
        embed.add_field(name="Before", value=before.content, inline=True)
    else:
        embed.add_field(name="Before", value="N/A", inline=True)
        cache.cache_message(payload.channel_id, after)
    embed.add_field(name="After", value=after.content, inline=True)

    await client.get_channel(references.message_channel_id).send(embed=embed)

@client.event
async def on_message(message: discord.Message):
    if message.author.id == client.user.id or message.channel.type != discord.ChannelType.text:
        return
    cache.cache_message(message.channel.id, message)
    for handler in handlers:
        if response := await handler.handle(message):
            command_cache.append({"message_id":message.id, "response":response})
            return
    
    #if message.content.startswith('hello'):
    #    await message.channel.send('Hello!')

async def on_close():
    logger.info(f'Stopping bot')
    await client.close()
    sys.exit(0)


client.run(references.token)