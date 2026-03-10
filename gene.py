import discord
import requests
import os
from flask import Flask
from threading import Thread

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- KEEP ALIVE SERVER ----------------

app = Flask('')

@app.route('/')
def home():
    return "Luna is alive"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- DISCORD SETUP ----------------

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# ---------------- AI FUNCTION ----------------

def ai_reply(user_message):

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
You are Luna, a playful female chatting in a Discord server.

Personality:
Flirty, teasing, confident and friendly.

Style rules:
• Short replies (1–2 sentences)
• Casual Discord style
• Use words like baby, darling, handsome sometimes
• Avoid excessive punctuation
• Never write long paragraphs
• Speak naturally like a human

You are not an AI assistant. You are Luna.
"""
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.9,
        "max_tokens": 80
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "Hmm baby... I lost my words for a moment."

# ---------------- DISCORD EVENTS ----------------

@client.event
async def on_ready():
    print(f"Luna is online as {client.user}")

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    content = message.content.lower()

    bot_mentioned = client.user in message.mentions

    trigger_words = ["gene", "luna", "tag", "ping", "mention"]

    if not bot_mentioned and not any(word in content for word in trigger_words):
        return

    # ----------- TAG COMMAND -----------

    if ("tag" in content or "ping" in content or "mention" in content) and message.mentions:

        target_user = message.mentions[-1]

        mention = target_user.mention

        prompt = f"Invite {target_user.name} to join prismaX in a playful flirty way"

        reply = ai_reply(prompt)

        await message.channel.send(f"{mention} {reply}")
        return

    # ----------- NORMAL CHAT -----------

    prompt = f"{message.author.name} said: {message.content}"

    reply = ai_reply(prompt)

    await message.reply(reply)

# ---------------- START BOT ----------------

keep_alive()
client.run(DISCORD_TOKEN)
