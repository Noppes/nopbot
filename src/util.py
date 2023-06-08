import discord
from collections import deque

class CachedMessages():    
    async def init(self, client: discord.Client):
        self.client = client
        self.message_cache = dict()
        
        for guild in client.guilds:
            member = guild.get_member(client.user.id)
            for channel in guild.channels:
                if channel.type == discord.ChannelType.text and channel.permissions_for(member).view_channel:
                    my_list = deque(maxlen=100)
                    async for message in channel.history():
                        my_list.append(message)
                    self.message_cache[channel.id] = my_list

    def get_cached_message(self, channel_id, message_id):
        if channel_id not in self.message_cache:
            return None
        messages = self.message_cache.get(channel_id)
        return next((obj for obj in messages if obj.id == message_id), None)

    def cache_message(self, channel_id, message):
        messages = self.message_cache.get(channel_id, False)
        if not messages:
            messages = deque(maxlen=100)
            self.message_cache[channel_id] = messages
        messages.append(message)