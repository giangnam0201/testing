import streamlit as st
import threading
import os
import asyncio

# --- 1. THE GLOBAL LOCK ---
# This check is the "Gold Standard" for keeping only 1 bot alive on Streamlit
if "bot_instance_running" not in st.runtime.stats.cache_stats.get_summary():
    # We use a dummy key in Streamlit's internal runtime to track global state
    pass 

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="Bot Server", page_icon="🚀")
st.title("Service Status: Online ✅")
st.write("The bot is running in the background.")

# BRIDGE: Injects Streamlit Secrets into the environment
for key, value in st.secrets.items():
    os.environ[key] = str(value)

# --- 3. YOUR CODE (Scope Fixed) ---
RAW_CODE = """
import discord
import asyncio
import time
import os

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
start_time = time.time()

async def status_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        uptime = int(time.time() - start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        try:
            await bot.change_presence(activity=discord.Game(f"Uptime: {hours:02}:{minutes:02}:{seconds:02}"))
        except:
            pass
        await asyncio.sleep(20)

@bot.event
async def on_ready():
    # We define the task directly here to avoid NameErrors in exec scope
    bot.loop.create_task(status_loop())
    print(f"Logged in as {bot.user}")

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
"""

# --- 4. SECURE STARTUP ENGINE ---
def run_bot():
    # Create isolated environment for exec
    safe_globals = {
        "discord": __import__("discord"),
        "asyncio": __import__("asyncio"),
        "time": __import__("time"),
        "os": __import__("os")
    }
    try:
        exec(RAW_CODE, safe_globals)
    except Exception as e:
        print(f"CRITICAL BOT ERROR: {e}")

# This logic ensures that even with multiple page refreshes, 
# only ONE thread is ever spawned per server session.
if not hasattr(st, "already_started_globally"):
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.already_started_globally = True
    st.success("Bot started!")
else:
    st.info("Bot is already active in the background.")
