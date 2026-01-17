import streamlit as st
import threading
import os
import asyncio
import sys

# --- 1. THE "ULTIMATE" GLOBAL LOCK ---
# We check if our custom 'bot_lock' exists in the system modules.
# This prevents the bot from starting twice, even if the page is refreshed.
if "bot_lock" not in sys.modules:
    sys.modules["bot_lock"] = True
    FIRST_RUN = True
else:
    FIRST_RUN = False

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="Bot Server", page_icon="🚀")
st.title("Service Status: Online ✅")
st.write("The bot is running in the background.")

# BRIDGE: Injects Streamlit Secrets into the environment
for key, value in st.secrets.items():
    os.environ[key] = str(value)

# --- 3. YOUR CODE ---
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
    # Define and start task in one go
    bot.loop.create_task(status_loop())
    print(f"Logged in as {bot.user}")

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
"""

# --- 4. STARTUP ENGINE ---
def run_bot():
    # Setup new loop for this specific background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Passing 'globals()' ensures functions can see each other
    exec(RAW_CODE, globals())

if FIRST_RUN:
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.success("🚀 Bot launched for the first time!")
else:
    st.info("ℹ️ Bot is already running in the background.")

# Show a small clock so the user knows the page is "alive"
st.divider()
st.caption(f"Last page refresh: {time.strftime('%H:%M:%S')}")
