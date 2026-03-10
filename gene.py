import discord
import requests
import os
import re
from flask import Flask
from threading import Thread

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- KEEP ALIVE ----------------

app = Flask('')

@app.route('/')
def home():
    return "Luna alive"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    Thread(target=run).start()

# ---------------- DISCORD ----------------

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# ---------------- AI FUNCTION ----------------

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
You are Luna, a playful flirty girl chatting on Discord.

Rules:
- Follow the instruction exactly
- Do NOT invent new topics
- Do NOT mention prismaX or anything unrelated
- Keep replies short
- Casual flirty tone
"""
            },
            {
                "role": "user",
                "content": f"Tell someone to: {instruction}"
            }
        ],
        "temperature": 0.8,
        "max_tokens": 60
    }

    r = requests.post(url, headers=headers, json=data)

    try:
        return r.json()["choices"][0]["message"]["content"]
    except:
        return instruction

# ---------------- MESSAGE EVENT ----------------

@client.event
async def on_ready():
    print("Luna online")

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    content = message.content.lower()

    triggers = ["tag", "ping", "mention"]

    if not any(t in content for t in triggers):
        return

    if message.mentions:
        
        target = message.mentions[0]
        mention = target.mention

        # extract instruction
        instruction = message.content

        instruction = re.sub(r"<@!?\d+>", "", instruction)
        instruction = re.sub(r"tag|ping|mention|and ask him to|and tell him to", "", instruction, flags=re.I)

        instruction = instruction.strip()

        reply = ai_reply(instruction)

        await message.channel.send(f"{mention} {reply}"
