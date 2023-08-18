import discord
faces = {
    ">.>":"<.<", "<.<":">.>", "<.>":">.<", ">.<":"<.>",
	">_>":"<_<", "<_<":">_>", "<_>":">_<", ">_<":"<_>", 
    "\o/":"\o/", "o/":"\o"
    }

async def handle(message: discord.Message):
    msg = message.content.lower().strip()
    for key in faces:
        if msg.endswith(key):
            return await message.channel.send(faces[key]) 
    return False