import discord
import requests
import os
from flask import Flask
from threading import Thread

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------- KEEP ALIVE SERVER ----------
app = Flask('')

@app.route('/')
def home():
    return "Luna is alive"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------- DISCORD SETUP ----------
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# ---------- AI FUNCTION ----------
def ai_reply(prompt):

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
You are Luna, a playful and confident female in a Discord server.

Personality:
You are flirty, playful, teasing and charming.
You like using words like baby, darling, handsome, cutie, love.

Rules:
Keep replies short (1-2 sentences).
Speak naturally like a real Discord user.
Avoid too many commas or punctuation.
Never sound like an AI assistant.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.9,
        "max_tokens": 80
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "Hmm baby... I lost my words for a second."

# ---------- DISCORD EVENTS ----------
@client.event
async def on_ready():
    print(f"Luna is online as {client.user}")

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    content = message.content.lower()

    triggers = ["gene", "luna", "tag", "ping", "mention"]

    bot_mentioned = client.user in message.mentions

    if not bot_mentioned and not any(word in content for word in triggers):
        return

    # ---------- TAGGING ----------
    if message.mentions and ("tag" in content or "ping" in content or "mention" in content):

        user = message.mentions[0]
        mention = user.mention

        prompt = f"Invite {user.name} to join prismaX in a flirty way"

        reply = ai_reply(prompt)

        await message.channel.send(f"{mention} {reply}")
        return

    # ---------- NORMAL CHAT ----------
    prompt = f"{message.author.name} said: {message.content}"

    reply = ai_reply(prompt)

    await message.reply(reply)


# ---------- START ----------
keep_alive()
client.run(DISCORD_TOKEN)
