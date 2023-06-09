import discord
import requests
from bs4 import BeautifulSoup

async def handle(message: discord.Message):
    if message.content.startswith("!anagram "):
        msg = message.content[9:].strip()
        if not msg:
            return False
        result = anagram(msg)
        if result:
            return await message.channel.send(result) 
    return False

def anagram(msg):
    max_size = int(500 / (len(msg) + 2))
    response = requests.get(f"https://new.wordsmith.org/anagram/anagram.cgi?t={max_size}&anagram=" + msg.replace(" ", "+"))
    if response.status_code != 200:
        return False

    soup = BeautifulSoup(response.text, 'html.parser')
    anagram_div = soup.find('blockquote')
    lines = anagram_div.text.strip().split('\n')
    anagrams = []
    start = False
    for line in lines:
        if start:
            if not line:
                break
            anagrams.append(line)
        if "Displaying" in line:
            start = True
        if "No anagrams found." in line:
            return "No anagram found"
            break
    return ", ".join(anagram.strip() for anagram in anagrams[:max_size])