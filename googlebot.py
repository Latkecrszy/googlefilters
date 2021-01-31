import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import string as st
import requests
import os
import dotenv

dotenv.load_dotenv()
TOKEN = os.environ.get("TOKEN", None)





bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Ready.")




@bot.command()
async def ping(ctx):
    await ctx.send(f"The ping is {round(bot.latency, 2)}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        pass
    else:
        raise error

bot.load_extension("search")

bot.run(TOKEN)
