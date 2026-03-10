import discord
import requests
import os
import re
from flask import Flask
from threading import Thread

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------- KEEP ALIVE ----------
app = Flask('')

@app.route('/')
def home():
    return "Luna alive"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    Thread(target=run).start()

# ---------- DISCORD ----------
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# ---------- AI ----------
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
You are Luna, a playful flirty girl chatting in a Discord server.

Personality:
Confident, teasing, playful.

Rules:
- Follow the instruction exactly.
- Do not invent new topics.
- Short replies (1 sentence).
- Flirty tone using words like baby, darling, handsome sometimes.
- Speak casually like a Discord user.
"""
            },
            {
                "role": "user",
                "content": instruction
            }
        ],
        "temperature": 0.9,
        "max_tokens": 60
    }

    r = requests.post(url, headers=headers, json=data)

    try:
        return r.json()["choices"][0]["message"]["content"]
    except:
        return instruction

# ---------- EVENTS ----------

@client.event
async def on_ready():
    print(f"Luna online as {client.user}")

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    content = message.content.lower()

    # Only trigger on tag commands
    if "tag" not in content:
        return

    # Ensure user actually mentioned someone
    if not message.raw_mentions:
        return

    target_id = message.raw_mentions[0]

    # prevent tagging itself
    if target_id == client.user.id:
        return

    target_user = await client.fetch_user(target_id)

    mention = f"<@{target_id}>"

    # extract instruction
    instruction = re.sub(r"<@!?\d+>", "", message.content)
    instruction = re.sub(r"tag|ask him|ask her|tell him|tell her|and", "", instruction, flags=re.I)
    instruction = instruction.strip()

    ai_text = ai_reply(f"Tell someone to: {instruction}")

    await message.channel.send(f"{mention} {ai_text}")

# ---------- START ----------
keep_alive()
client.run(DISCORD_TOKEN)
