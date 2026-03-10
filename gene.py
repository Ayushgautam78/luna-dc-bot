import discord
import requests
import os
import threading
from flask import Flask

TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# -------- Flask server for uptime pings -------- #

app = Flask(__name__)

@app.route("/")
def home():
    return "Gene bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# -------- AI reply using Groq -------- #

def ai_reply(message):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": "You are Gene, a playful flirty girl chatting in a Discord server. Speak casually and affectionately using words like baby, darling, sweetheart, love and handsome. Keep replies short and playful."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 1,
        "max_tokens": 80
    }

    r = requests.post(url, headers=headers, json=data)
    result = r.json()

    return result["choices"][0]["message"]["content"]

# -------- Discord events -------- #

@client.event
async def on_ready():
    print(f"Gene is online as {client.user}")

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    text = message.content.lower()

    trigger_words = ["gene", "ping", "tag", "mention", "hey gene"]

    if any(word in text for word in trigger_words) or client.user in message.mentions:

        reply = ai_reply(message.content)

        await message.reply(reply)

# -------- Start both servers -------- #

threading.Thread(target=run_web).start()

client.run(TOKEN)