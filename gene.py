import discord
import requests
import os
import threading
from flask import Flask
import re
TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# -------- Flask server for uptime pings -------- #

app = Flask(__name__)

@app.route("/")
def home():
    return "Homeless Girl bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# -------- Crypto APIs -------- #

def get_crypto_price(query):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/search?query={query}", headers=headers).json()
        if r.get("coins"):
            coin_id = r["coins"][0]["id"]
            name = r["coins"][0]["name"]
            
            rank = r["coins"][0].get("market_cap_rank", "N/A")
            
            p = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_market_cap=true&include_24hr_change=true", headers=headers).json()
            if coin_id in p:
                data = p[coin_id]
                usd_price = data.get("usd", "N/A")
                
                market_cap = data.get("usd_market_cap", "N/A")
                if isinstance(market_cap, (int, float)): market_cap = f"${market_cap:,.0f}"
                
                price_change_24h = data.get("usd_24h_change", "N/A")
                if isinstance(price_change_24h, (int, float)): price_change_24h = round(price_change_24h, 2)
                
                info = f"**{name}** (Rank: {rank})\n"
                info += f"💰 **Price:** ${usd_price} USD\n"
                info += f"📊 **Market Cap:** {market_cap}\n"
                info += f"📅 **24h Change:** {price_change_24h}%"
                
                return info
    except Exception as e:
        print(f"CoinGecko Error fetching price: {e}", flush=True)
        
    # Fallback to DexScreener if CoinGecko is rate-limiting
    try:
        d_res = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={query}", headers=headers).json()
        
        if d_res.get("pairs"):
            pair = d_res["pairs"][0]
            name = pair.get("baseToken", {}).get("name", query.upper())
            symbol = pair.get("baseToken", {}).get("symbol", query.upper())
            
            usd_price = pair.get("priceUsd", "N/A")
            if usd_price != "N/A":
                usd_price = round(float(usd_price), 4) if float(usd_price) > 0.0001 else float(usd_price)
                
            change = pair.get("priceChange", {}).get("h24", "N/A")
            market_cap = pair.get("marketCap", "N/A")
            fdv = pair.get("fdv", "N/A")
            
            if isinstance(market_cap, (int, float)) and market_cap > 0: market_cap = f"${int(market_cap):,}"
            elif market_cap == 0: market_cap = "N/A"
                
            if isinstance(fdv, (int, float)) and fdv > 0: fdv = f"${int(fdv):,}"
            elif fdv == 0: fdv = "N/A"
            
            info = f"**{name} ({symbol})** (DEX Data)\n"
            info += f"💰 **Price:** ${usd_price}\n"
            if market_cap != "N/A": info += f"📊 **Market Cap:** {market_cap}\n"
            if fdv != "N/A": info += f"📈 **FDV:** {fdv}\n"
            info += f"📅 **24h Change:** {change}%"
            
            return info
    except Exception as e:
        print(f"DexScreener Error fetching price: {e}", flush=True)

    return f"I couldn't find any data for `{query}`! (The crypto APIs might be blocking me right now)"

def get_crypto_news():
    try:
        r = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN").json()
        news = r.get("Data", [])[:6]
        if news:
            headlines = [f"• {n['title']}" for n in news]
            return "**Latest Crypto News (Top 6):**\n" + "\n".join(headlines)
    except Exception as e:
        print(f"Error fetching news: {e}", flush=True)
    return "I couldn't fetch the news right now!"

# -------- AI reply using Groq -------- #

def ai_reply(message):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    user_content = f"{message.author.display_name} says: {message.content}"

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": "You are Homeless Girl, a playful flirty girl chatting in a Discord server. Speak casually and affectionately using words like baby, darling, sweetheart, love and handsome. Keep replies short and playful. IMPORTANT RULES: 1) NEVER EVER output a Discord tag like <@12345678> in your response unless the user EXPLICITLY commands you to 'tag' someone. 2) NEVER tag yourself."
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        "temperature": 1,
        "max_tokens": 150
    }

    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code != 200:
            print(f"Groq API Error: {r.status_code} - {r.text}", flush=True)
            return "Oops! I'm having a little brain freeze right now. 🧊"
        
        result = r.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error in ai_reply: {e}", flush=True)
        return "Oops! I couldn't think of a reply right now, baby. 🥺"

# -------- Discord events -------- #

@client.event
async def on_ready():
    print(f"Homeless Girl is online as {client.user}", flush=True)

@client.event
async def on_message(message):
    print(f"[DEBUG] Event triggered by {message.author}", flush=True)

    if message.author == client.user:
        return

    text = message.content.lower()

    print(f"[DEBUG] Received message from {message.author}: '{text}'", flush=True)

    trigger_words = ["homeless girl", "ping", "tag", "mention", "hey homeless girl"]

    is_directed_at_bot = any(word in text for word in trigger_words) or client.user in message.mentions
    has_token = bool(re.search(r'\$([a-zA-Z0-9\-]+)', text))
    has_news = "news" in text and is_directed_at_bot
    has_price = "price" in text and is_directed_at_bot

    # Handle crypto-specific commands (Bypass AI entirely)
    if has_token or has_price:
        queries = []
        token_matches = re.findall(r'\$([a-zA-Z0-9\-]+)', text)
        queries.extend(token_matches)
        
        if not queries and is_directed_at_bot:
            price_match = re.search(r'price\s+(?:of|for)?\s*([a-zA-Z0-9\-]+)', text)
            if price_match:
                queries.append(price_match.group(1))

        if queries:
            replies = []
            for query in set(queries):
                replies.append(get_crypto_price(query))
            await message.reply("\n\n".join(replies))
            return
            
    if has_news:
        await message.reply(get_crypto_news())
        return

    # Handle AI Chat
    if is_directed_at_bot:
        reply = ai_reply(message)
        await message.reply(reply)

# -------- Start both servers -------- #

threading.Thread(target=run_web).start()

client.run(TOKEN)
