import discord
import requests
import os
import re
from flask import Flask
from threading import Thread

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------- KEEP ALIVE (FOR RENDER) ----------
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

# ---------- AI FUNCTION ----------
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
You are Luna, a playful flirty girl chatting in Discord.

Rules:
- Follow the instruction exactly.
- Do NOT change topic.
- Reply in ONE short sentence.
- Be slightly flirty using words like baby, darling, handsome.
- Speak casually like a Discord user.
"""
            },
            {
                "role": "user",
                "content": instruction
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


# ---------- EVENTS ----------
@client.event
async def on_ready():
    print(f"Luna online as {client.user}")


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    content = message.content.lower()

    # Trigger only when user says tag
    if "tag" not in content:
        return

    # Ensure someone was mentioned
    if not message.mentions:
        return

    target_user = message.mentions[0]

    # Prevent bot tagging itself
    if target_user.id == client.user.id:
        return

    mention = target_user.mention

    # Extract instruction text
    instruction = re.sub(r"<@!?\d+>", "", message.content)
    instruction = re.sub(r"tag|ask him|ask her|tell him|tell her|and", "", instruction, flags=re.I)
    instruction = instruction.strip()

    if instruction == "":
        return

    ai_text = ai_reply(instruction)

    await message.channel.send(f"{mention} {ai_text}")


# ---------- START ----------
keep_alive()
client.run(DISCORD_TOKEN)
