################################## Imports #####################################

import os
import pytz
import asyncio
import discord
import datetime

from pydub import AudioSegment
from discord import FFmpegPCMAudio
from discord.ext import tasks, commands
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone

############################## Global Variables ################################

current_gong = None
INTRO = AudioSegment.from_mp3("audio/INTRODUCTION.mp3")
GONG = AudioSegment.from_mp3("audio/GONG.mp3")
FINAL = AudioSegment.from_mp3("audio/FINAL.mp3")

# Loads variables stored in file `.env`
load_dotenv()

intents = discord.Intents.default()
intents.members = True

# Setup the bot.
bot = commands.Bot(command_prefix = "!", intents=intents)

############################### Helper Methods #################################

# Helper function to get PST Time and return the current hour.
def get_pst_hour():
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone("US/Pacific"))

    # Return the current hour.
    if date.hour > 12:
        return date.hour - 12
    else:
        return date.hour


# Helper function generates current gong.
def make_gong():
    # Get how many hours (gongs) to play.
    hours = get_pst_hour()

    # Reset the current_gong to the intro.
    current_gong = INTRO

    # Queue up every gong up until the last.
    for i in range(hours - 1):
        current_gong += GONG
    
    # Queue up the final gong.
    current_gong += FINAL

    # Export custom gong to file, `CURRENT.mp3`.
    current_gong.export("audio/CURRENT.mp3", format="mp3")


############################### Client Methods #################################


# Debugging event.
@bot.event
async def on_ready():
    print("Big-Ben-Bot is ready!")
    print("---------------------") 


# Print a short introduction to chat.
@bot.command()
async def start(ctx):
    hourly_gong.start(ctx)
    await ctx.send("Tik Tok! You'll be hearing from me every hour!")


# Print a short introduction to chat.
@bot.command()
async def hello(ctx):
    await ctx.send("Hello, I am Big-Ben-Bot!")


# Joins voice channel.
@bot.command(pass_context = True)
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()

        # Generate the file, `CURRENT.mp3` which has the current hour in gongs.
        make_gong()
        
        # Play the created audio.
        voice.play(FFmpegPCMAudio("audio/CURRENT.mp3"))

        # FIXME: Simple wait, fix with multi-threading?
        while voice.is_playing():
                continue

        # Leave the channel.
        await voice.disconnect()

        # Delete the file once done.
        os.remove("audio/CURRENT.mp3")
    else:
        await ctx.send("GONG! You're not in a voice channel!")


# Leaves voice channel.
@bot.command(pass_context = True)
async def leave(ctx):
    if ctx.voice_client:
        channel = await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("GONG! I'm not in a voice channel!")


@tasks.loop(minutes=5)
async def hourly_gong(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()

        # Generate the file, `CURRENT.mp3` which has the current hour in gongs.
        make_gong()
        
        # Play the created audio.
        voice.play(FFmpegPCMAudio("audio/CURRENT.mp3"))

        # FIXME: Simple wait, fix with multi-threading?
        while voice.is_playing():
                continue

        # Leave the channel.
        await voice.disconnect()

        # Delete the file once done.
        os.remove("audio/CURRENT.mp3") 

bot.run(os.getenv("DISCORD_TOKEN"))