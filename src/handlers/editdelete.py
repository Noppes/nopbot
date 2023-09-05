import discord
from discord.ext import tasks, commands
import random
import references


class EditDeleteCog(commands.Cog):

    def __init__(self, bot, logger, cache):
        self.logger = logger
        self.bot = bot
        self.cache = cache
        self.channel = bot.get_channel(references.message_history_channel_id)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        await self.cache.delete_command(payload.message_id)

        if not (message := payload.cached_message) and not (message := cache.get_cached_message(payload.channel_id, payload.message_id)):
            return

        embed = discord.Embed(
            title = "Message Deleted from #" + self.bot.get_channel(payload.channel_id).name ,
            description = message.content,
            color = discord.Color.red(),
            timestamp = message.created_at
        )
        embed.set_author(name=message.author.display_name + f" (ID: {message.author.id})", icon_url=message.author.avatar.url, url=message.author.avatar.url)
        if message.attachments:
            embed.add_field(name="Attachements",  value="\n".join(["- " + item.url for item in message.attachments]), inline=False)


        embed.timestamp = message.created_at
        if message.author.id != message.author.id:
            responsible_user = self.bot.get_user(payload.cached_message.author.id)
            if responsible_user:
                embed.add_field(name="Deleted By", value=responsible_user.name)

        await self.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        channel = self.bot.get_channel(payload.channel_id)
        after = await channel.fetch_message(payload.message_id)
        if after.author.id == self.bot.user.id:
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

        await self.channel.send(embed=embed)


