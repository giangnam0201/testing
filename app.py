import streamlit as st
import threading
import os
import asyncio

# --- 1. GLOBAL CHECK ---
# This exists outside the Streamlit "run" cycle to prevent restarts
if not hasattr(st, "bot_is_running"):
    st.bot_is_running = False

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="Bot Server", page_icon="🚀")
st.title("Service Status: Online ✅")
st.write("The bot is running in the background.")
st.info("The bot will NOT restart when you refresh this page.")

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
        await bot.change_presence(activity=discord.Game(f"Uptime: {hours:02}:{minutes:02}:{seconds:02}"))
        await asyncio.sleep(15) # Increased sleep to prevent rate limits

@bot.event
async def on_ready():
    # Using modern task creation for stability
    asyncio.create_task(status_loop())
    print(f"Logged in as {bot.user}")

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
"""

# --- 4. SERVER-WIDE STARTUP ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        exec(RAW_CODE)
    except Exception as e:
        print(f"Bot error: {e}")

# Only start if the GLOBAL variable is False
if not st.bot_is_running:
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.bot_is_running = True
    st.success("Bot process initialized!")
else:
    st.write("✔️ Bot process is already active in the background.")
