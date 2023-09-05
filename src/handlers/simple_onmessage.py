import discord
from discord.ext import tasks, commands
import random


class SimpleOnMessageCog(commands.Cog):

    def __init__(self, bot, logger, cache):
        self.logger = logger
        self.bot = bot
        self.cache = cache
        self.faces = {
            ">.>":"<.<", "<.<":">.>", "<.>":">.<", ">.<":"<.>",
            ">_>":"<_<", "<_<":">_>", "<_>":">_<", ">_<":"<_>", 
            "\o/":"\o/", "o/":"\o", "\o":"o/"
            }
        self.face_history = {}
        self.repeat_history = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        response = await self.handle_faces(message)
        if not response:
            response = await self.handle_repeat(message)
        self.cache.cache_command_message(message, response)
    
    async def handle_faces(self, message: discord.Message):
        msg = message.content.lower().strip()        
        for key in self.faces:
            if msg.endswith(key):
                last_triggered = self.face_history.get(message.channel, False)
                if last_triggered == self.faces[key] or last_triggered == key:
                    return False
                self.face_history[message.channel] = key
                return await message.channel.send(self.faces[key]) 
        self.face_history[message.channel] = False
        
    async def handle_repeat(self, message: discord.Message):
        ctx = await self.bot.get_context(message)
        if ctx.valid and ctx.command:
            return False

        msg = message.content.lower().strip()
        if message.channel.id not in self.repeat_history:
            self.repeat_history[message.channel.id] = (msg, [message.content])
            return False

        (msg2, messages) = self.repeat_history[message.channel.id]
        if len(msg) > len(msg2):
            msg, msg2 = (msg2, msg)
            
        if msg not in msg2 or len(msg2) > len(msg) * 2:
            self.repeat_history[message.channel.id] = (message.content.lower().strip(), [message.content])
            return False
        messages.append(message.content)
        self.repeat_history[message.channel.id] = (msg, messages)
        if len(messages) == 3:
            return await message.channel.send(random.choice(messages))  


