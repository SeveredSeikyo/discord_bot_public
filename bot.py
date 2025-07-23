import discord
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

print(CHANNEL_ID)

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

joke_task = None
url = os.getenv("URL")

async def fetch_joke():
    global url
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()  # assuming JSON response
                return data.get("joke")  # adjust based on your API response
            else:
                return f"Failed to fetch joke: HTTP {resp.status}"

async def joke_loop():
    await bot.wait_until_ready()
    
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"❌ Channel with ID {CHANNEL_ID} not found.")
        return  # Exit the task if channel isn't found

    while True:
        joke = await fetch_joke()
        await channel.send(joke or "No joke found.")
        await asyncio.sleep(3600)


@bot.slash_command(name="start", description="Start hourly joke delivery.")
async def start(ctx):
    global joke_task
    if joke_task is None:
        await ctx.respond("Starting joke loop! 🎭")
        joke_task = asyncio.create_task(joke_loop())
    else:
        await ctx.respond("Joke loop already running.")

@bot.slash_command(name="stop", description="Stop hourly joke delivery.")
async def stop(ctx):
    global joke_task
    if joke_task:
        joke_task.cancel()
        joke_task = None
        await ctx.respond("Joke loop stopped. 🛑")
    else:
        await ctx.respond("Joke loop is not running.")

@bot.slash_command(name="joke", description="Retrieve a Dad Joke.")
async def joke(ctx):
    try:
        await ctx.respond("Fetching Joke...")
        joke = await fetch_joke()  # Assuming you have a function to get joke
        await ctx.send_followup(joke or "No joke found.")
    except Exception as e:
        await ctx.respond("❌ Error Fetching Joke.")
        print(f"Error in /joke command: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    await bot.sync_commands()
    print(f"{bot.user} is online with slash commands synced.")

    


bot.run(TOKEN)
