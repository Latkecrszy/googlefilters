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

bot.remove_command("help")


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


@bot.command()
async def help(ctx):
    embed = discord.Embed(title=f"How Google Filters Works",
                          description=f"**Google Filters is a bot that aims to solve the problem of painstakingly picking through your google searches to find some from the source you want. Find out how to use it here!**")
    embed.add_field(name=f"Google Filters is super simple to use.",
                    value="All you need to do is type `!search <whatever you want to search for>`. The bot will then guide your through the process of selecting and setting up your filters, and display the final page to you at the end! That's it! Enjoy the bot!")
    await ctx.send(embed=embed)

bot.load_extension("search")

bot.run(TOKEN)
