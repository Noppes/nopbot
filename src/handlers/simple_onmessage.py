import discord
from discord.ext import tasks, commands
import random
from openai import AsyncOpenAI
import references
import datetime


class SimpleOnMessageCog(commands.Cog):

    def __init__(self, bot, logger, cache):
        self.logger = logger
        self.bot = bot
        self.cache = cache
        self.openai_enabled = False
        self.openai_channels = {}
        if references.openai_key != 'your_key' and references.openai_key:
            self.openai_enabled = True
            self.chatbot = AsyncOpenAI(
                api_key=references.openai_key,
            )
        self.faces = {
            ">.>":"<.<", "<.<":">.>", "<.>":">.<", ">.<":"<.>",
            ">_>":"<_<", "<_<":">_>", "<_>":">_<", ">_<":"<_>", 
            "\o/":"\o/", "o/":"\o", "\o":"o/", "o7":"o7"
            }
        self.face_history = {}
        self.repeat_history = {}
        
        self.question_keywords = ("should ", "will ", "do ", "am i ", "does ", "are ", "did ", "is ", "that ", "were ", "does ", "was ")
        self.question_responses = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes - definitely",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "No",
            "Signs point to yes",
            "Ask again later",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful"
        ]
        self.version_pattern = r"\d+(\.\d+)+"
        self.update_responses = [
            "Have you read frequently asked questions?",
            "Noppes has been busy with work, but is still working on this mods",
            "Noppes is still updating to newer version",
            "Updating mods is quite time-consuming, it's still being worked on",
            "Somebody didnt read the rules",
        ]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ctx = await self.bot.get_context(message)
        if ctx.valid and ctx.command or message.author.id == self.bot.user.id:
            return
        response = await self.ai_response(message)
        if not response:
            response = await self.on_question(message)
        if not response:
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
        return False
        
    async def handle_repeat(self, message: discord.Message):
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
        return False

    async def ai_response(self, message: discord.Message):
        if not self.openai_enabled or ('nopbot' not in message.clean_content.lower().strip() and not await self._is_reply(message)):
            return False
        MSGS = [ 
            {"role": "system", "content": references.openai_prompt}
        ]
        now = datetime.datetime.now()
        if message.channel.id in self.openai_channels:
            (history, timestamp) = self.openai_channels[message.channel.id]
            if (now - timestamp).total_seconds() / 60 < 15: #if last response was no more than 15 min old use it
                MSGS = history

        MSGS.append({"role": "user", "content": f"the user {message.author.display_name} says: {message.clean_content}" })

        try:
            response = await self.chatbot.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=MSGS,
                max_tokens=100,
                temperature=0.7
            )
            response = response.choices[0].message.content
            MSGS.append({"role": "assistant", "content": response})
            self.openai_channels[message.channel.id] = (MSGS, now)
            return await message.channel.send(response)  
        except Exception as e:
            self.logger.exception(e)
            return False

    async def _is_reply(self, message: discord.Message):
        if message.reference is None or message.type != discord.enums.MessageType.reply:
            return False
        ctx = await self.bot.get_context(message)
        cm = await ctx.fetch_message(message.reference.message_id)
        return cm.author.id == self.user.id
        
    async def on_question(self, message: discord.Message):
        msg = message.content.lower().strip()

        if msg.endswith("?") and "update" in msg and ("mod" in msg or "npc" in msg or "mpm" in msg or self.contains_number(msg)):
            return await message.channel.send(random.choice(self.update_responses))

        if message.channel.type == discord.enums.ChannelType.forum:
            return False

        # elif msg.endswith("?") and msg.startswith(self.question_keywords):
        #     return await message.channel.send(random.choice(self.question_responses))

        return False
        
        
    def contains_number(self, string):
        return bool(re.search(self.version_pattern, string))


