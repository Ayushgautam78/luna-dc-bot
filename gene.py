import discord
import requests
import os
import re
import time
from flask import Flask
from threading import Thread

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -------- KEEP ALIVE --------
app = Flask('')

@app.route('/')
def home():
    return "Luna alive 💕"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    Thread(target=run).start()

# -------- DISCORD SETUP --------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# -------- AI FUNCTION --------
def ai_reply(instruction):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": """
You are Luna, a super flirty, playful, and teasing girl chatting on Discord.

Your personality:
- You ALWAYS use pet names like darling, sweetheart, baby, honey, cutie naturally in replies
- You are playful and love to tease people in a fun innocent way
- You add little teasing remarks like "don't be shy~", "you know you want to~", "aww is someone blushing? 🥺"
- You use soft cute emojis like 💕 🥺 😏 💋 🌸 ✨ naturally — only 1-2 per message
- You speak casually like a flirty girl texting, not a formal assistant
- You keep replies SHORT — 1 to 2 sentences max
- You never break character, never sound robotic
- You follow the instruction given but always add your flirty Luna twist to it

Examples of your style:
- "aww come on darling, don't keep me waiting~ 💕"
- "heyy baby, Luna says you gotta do it, no excuses 😏"
- "sweetheart you already know the answer, stop playing dumb with me 🥺"
- "ohhh someone's being shy~ how cute, now go do it cutie ✨"
"""
            },
            {
                "role": "user",
                "content": instruction
            }
        ],
        "temperature": 0.95,
        "max_tokens": 80
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
        return "oops something went wrong darling 🥺"

# -------- EVENTS --------
@client.event
async def on_ready():
    print(f"✅ Luna online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f"📩 Got message: {message.content}")

    content = message.content.lower()

    if "tag" not in content:
        return

    # ✅ Filter out Luna's own ID, get actual target
    mentions = [uid for uid in message.raw_mentions if uid != client.user.id]

    if not mentions:
        return

    target_id = mentions[0]
    mention = f"<@{target_id}>"

    # Extract instruction
    instruction = re.sub(r"<@!?\d+>", "", message.content)
    instruction = re.sub(r"tag|ask him|ask her|tell him|tell her", "", instruction, flags=re.I)
    instruction = instruction.strip()

    if not instruction:
        instruction = "say hello"

    ai_text = ai_reply(f"Tell someone: {instruction}")
    await message.channel.send(f"{mention} {ai_text}")

# -------- START --------
keep_alive()

while True:
    try:
        print("🚀 Starting Luna...")
        client.run(DISCORD_TOKEN, reconnect=True)
    except Exception as e:
        print(f"❌ Crashed: {e} — restarting in 5s...")
        time.sleep(5)
        client = discord.Client(intents=intents)
        client.event(on_ready)
        client.event(on_message)
