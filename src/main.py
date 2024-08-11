import discord
from discord.ext import tasks, commands
import util
import references
import signal
import sys
import asyncio
import logging
import handlers
from collections import deque

from handlers.anagram import AnagramCog
from handlers.dict_ import DictCog
from handlers.editdelete import EditDeleteCog
from handlers.flip import FlipCog
from handlers.mc import MinecraftCog
from handlers.humble import HumbleCog
from handlers.meme import MemeCog
from handlers.quote import QuoteCog
from handlers.simple_commands import SimpleCommandsCog
from handlers.simple_onmessage import SimpleOnMessageCog

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True 

logger = logging.getLogger("nopbot")
logFormatter = logging.Formatter("[%(asctime)s] [%(filename)s(%(lineno)d)] [%(levelname)s] %(message)s",'%y-%m-%d %H:%M:%S')
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.setLevel(logging.INFO)
logger.addHandler(consoleHandler) 

client = commands.Bot("!", intents=intents)
cache = util.CachedMessages()

def log_exception(self, exc_type, exc_value, exc_traceback):
    logger.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = log_exception

@client.event
async def on_ready():
    logger.info(f'Discord.py {discord.__version__}')
    logger.info(f'We have logged in as {client.user}')
    client.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(on_close()))
    await cache.init(client)
    await client.add_cog(AnagramCog(client, logger))
    await client.add_cog(DictCog(client, logger))
    await client.add_cog(EditDeleteCog(client, logger, cache))
    await client.add_cog(FlipCog(client, logger, cache))
    await client.add_cog(MinecraftCog(client, logger, cache))
    await client.add_cog(HumbleCog(client, logger, cache))
    await client.add_cog(MemeCog(client, logger))
    await client.add_cog(QuoteCog(client, logger))
    await client.add_cog(SimpleCommandsCog(client, logger, cache))
    await client.add_cog(SimpleOnMessageCog(client, logger, cache))
    logger.info(f'Finished building cache')

@client.event
async def on_message(message: discord.Message):
    if message.author.id == client.user.id or message.channel.type != discord.ChannelType.text:
        return
    cache.cache_message(message.channel.id, message)
    await client.process_commands(message)

async def on_close():
    logger.info(f'Stopping bot')
    await client.close()
    sys.exit(0)

client.run(references.token)