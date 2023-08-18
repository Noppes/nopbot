import discord
history = {}

async def handle(message: discord.Message):
    msg = message.content.lower().strip()
    if message.channel.id not in history:
        history[message.channel.id] = (msg, 1)
        return False

    (msg2, count) = history[message.channel.id]
    if len(msg) > len(msg2):
        msg, msg2 = (msg2, msg)
        
    if msg not in msg2 or len(msg2) > len(msg) * 2:
        history[message.channel.id] = (message.content.lower().strip(), 1)
        return False

    count += 1
    history[message.channel.id] = (msg, count)
    if count == 3:
        return await message.channel.send(msg.capitalize())  