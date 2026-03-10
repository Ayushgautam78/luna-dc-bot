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
You are Luna, a playful flirty female chatting in a Discord server.

Rules:
- Keep replies short (1 sentence mostly)
- Speak casually like a real Discord user
- Slightly flirty tone
- Avoid repeating the same phrases
- Avoid too many punctuation marks
- Always follow the context of the message

If someone asks you to tag someone and say something, you must say exactly that idea but in your own playful style.
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
        return "hmm baby my brain lagged for a second"

# ---------------- DISCORD EVENTS ----------------

@client.event
async def on_ready():
    print(f"Luna online as {client.user}")

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    content = message.content.lower()

    triggers = ["tag", "ping", "mention", "luna", "gene"]

    bot_mentioned = client.user in message.mentions

    if not bot_mentioned and not any(word in content for word in triggers):
        return

    # ---------------- TAG COMMAND ----------------

    if message.mentions and ("tag" in content or "ping" in content or "mention" in content):

        # get the person user actually tagged
        target_user = message.mentions[0]

        mention = target_user.mention

        prompt = f"""
User {message.author.name} said:
"{message.content}"

Reply naturally as Luna and tag {target_user.name}.
Follow the instruction in the message context.
"""

        reply = ai_reply(prompt)

        await message.channel.send(f"{mention} {reply}")
        return

    # ---------------- NORMAL CHAT ----------------

    prompt = f"{message.author.name} said: {message.content}"

    reply = ai_reply(prompt)

    await message.reply(reply)

# ---------------- START BOT ----------------

keep_alive()
client.run(DISCORD_TOKEN)
