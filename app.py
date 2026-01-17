import streamlit as st
import threading
import sys
import io

# --- STREAMLIT KEEP-ALIVE UI ---
st.title("Keep-Alive Page")
st.write("The background process is running.")
st.status("System Active", state="running")

# --- PASTE YOUR WHOLE CODE INSIDE THE BOX BELOW ---
RAW_CODE = """
import discord
import asyncio
import time

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
    bot.loop.create_task(status_loop())
    print(f"Logged in as {bot.user}")

bot.run("MTQ0MjAwNTM4OTIxMzQzMzg1Nw.GnBwFG.v4tkQbSrP4Kp11tG_mxYTMqrBpaoEyDICal7v0")
"""
# --- END OF YOUR CODE BOX ---

def run_background_process():
    # This executes your code exactly as written in a background thread
    exec(RAW_CODE, {})

if "process_started" not in st.session_state:
    thread = threading.Thread(target=run_background_process, daemon=True)
    thread.start()
    st.session_state.process_started = True
    st.success("Background process started successfully!")
else:
    st.info("Process is already running in the background.")
