import streamlit as st
import threading
import os
import asyncio

# --- 1. STREAMLIT UI (Keep-Alive) ---
st.set_page_config(page_title="Discord Bot Host", page_icon="🤖")
st.title("Bot Status: Online ✅")
st.write("The bot is running in the background.")
st.caption("Uptime tracking is active on Discord presence.")

# BRIDGE: Injects Streamlit Secrets into the environment
for key, value in st.secrets.items():
    os.environ[key] = str(value)

# --- 2. YOUR CODE (Modified for Secrets) ---
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
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    # Note: Modern discord.py uses asyncio.create_task or similar 
    # but we keep your original logic here
    asyncio.create_task(status_loop())
    print(f"Logged in as {bot.user}")

# GET TOKEN FROM SECRET
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
"""

# --- 3. BACKGROUND EXECUTION ---
def run_bot():
    # Setup new loop for the background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    exec(RAW_CODE, {"asyncio": asyncio})

if "bot_running" not in st.session_state:
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.session_state.bot_running = True
