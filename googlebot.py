import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import aiohttp
import string as st
import requests
import os
import dotenv

dotenv.load_dotenv()
TOKEN = os.environ.get("TOKEN", None)


def find_all(string, filters=None):
    string = string.split('<a href="/url?q=')
    found = {}
    for i in string:
        if i.startswith("https://") and '">' in i:
            link = i.split('">')
            link_parts = link[0].split(".")
            dotNum = len([d for d in link[0].split("/")[0] if d == "."])
            link_extension = link_parts[dotNum].split("/")[0]
            link_site = link_parts[1]
            name = link[3].split("</div>")
            passed = True
            # filters = {"true": {"extension": ["org", "gov", "com"]}, {"site": ["wikipedia", "merriam-webster"]}}, "false": {"site": ["youtube"]}}
            if filters is not None:
                if 'true' in filters:
                    if 'extension' in filters['true']:
                        passed = False if link_extension not in filters['true']['extension'] else True
                    if 'site' in filters['true']:
                        passed = False if link_site not in filters['true']['site'] else True
                if 'false' in filters:
                    if 'extension' in filters['false']:
                        passed = False if link_extension in filters['false']['extension'] else True
                    if 'site' in filters['false']:
                        passed = False if link_site in filters['false']['site'] else True

            if passed:
                for j in st.ascii_uppercase:
                    if j in name[0] and "<" not in name[0]:
                        if "\n" in name[0]:
                            name = "".join(name[0].split("\n"))
                        found[(link[0].split("&")[0])] = name
                        break

    return found


bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Ready.")


@bot.command()
async def search(ctx, *, article):
    original = article
    article = article.replace(" ", "+")
    article = f"https://google.com/search?q={article}"
    page = requests.get(article)
    soup = BeautifulSoup(page.content, 'html.parser')
    filters = {}

    def check(m):
        return m.author == ctx.author and not m.author.bot
    more = ''
    while True:
        await ctx.send(
            f"Would you like to apply any {more} filters to your search? If yes, please send the name of the filter. (`extension` or `site`.) If no, send `no`.")
        more = "more"
        message = await bot.wait_for("message", check=check)
        if "no" in message.content.lower():
            if more == '':
                filters = None
            break
        elif "extension" in message.content.lower():
            await ctx.send(f"Ok, you have selected the extension filter. Please tell me whether or not you would like to only accept this extension or block this extension fro your search results. (`accept`/`block`")
            message = await bot.wait_for("message", check=check)
            if "accept" in message.content.lower():
                await ctx.send(f"You have selected that you will only receive results from this extension. Please send the extension that you would like to receive results from.")
                message = await bot.wait_for("message", check=check)
                if 'true' not in filters:
                    filters['true'] = {}
                if 'extensions' not in filters['true']:
                    filters['true']['extensions'] = []
                filters['true']['extensions'].append(message.content.lower())
            elif "block" in message.content.lower():
                await ctx.send(f"You have selected that you will not receive results from this extension. Please send the extension that you would like to block results from.")
                message = await bot.wait_for("message", check=check)
                if 'false' not in filters:
                    filters['false'] = {}
                if 'extensions' not in filters['false']:
                    filters['false']['extensions'] = []
                filters['false']['extensions'].append(message.content.lower())
        elif "site" in message.content.lower():
            await ctx.send(
                f"You have selected that you will only receive results from this site. Please send the name of the site that you would like to receive results from.")
            message = await bot.wait_for("message", check=check)
            if 'true' not in filters:
                filters['true'] = {}
            if 'site' not in filters['true']:
                filters['true']['site'] = []
            filters['true']['site'].append(message.content.lower())
        elif "block" in message.content.lower():
            await ctx.send(
                f"You have selected that you will not receive results from this site. Please send the name of the site that you would like to block results from.")
            message = await bot.wait_for("message", check=check)
            if 'false' not in filters:
                filters['false'] = {}
            if 'site' not in filters['false']:
                filters['false']['site'] = []
            filters['false']['site'].append(message.content.lower())

    links = find_all(str(soup), filters)
    """async with aiohttp.ClientSession() as cs:
        async with cs.get(article) as r:
            res = await r.text()
            print(res)
            print(article)
            links = find_all(res)"""
    # print(soup.prettify())
    print(links)
    if links:
        embed = discord.Embed(title=f"Results for {original}")
        for key, value in links.items():
            embed.add_field(name=value[0], value=f"[Link]({key})", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=discord.Embed(description=f"Sorry, it seems as if google couldn't find any results for your search. Make sure you've spelled everything correctly, and try again!"))





bot.run(TOKEN)
