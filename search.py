from discord.ext import commands
import random, requests, discord, asyncio
import string as st
from bs4 import BeautifulSoup


def find_all(string, filters=None):
    string = string.split('<a href="/url?q=')
    found = {}
    for i in string:
        if i.startswith("https://") and '">' in i:
            link = i.split('">')
            link_parts = link[0].split(".")
            dotNum = len([d for d in link[0].split("/")[2] if d == "."])
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



class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def request(self, article):
        return requests.get(article)

    @commands.command()
    async def search(self, ctx, *, article):
        original = article
        article = article.replace(" ", "+")
        filters = {}

        def check(m):
            return m.author == ctx.author and not m.author.bot

        more = ''
        while True:
            await ctx.send(
                f"Would you like to apply any {more}filters to your search? If you would, please send the name of the filter. The names of the available filters are `extension` and `website` If you would not like to apply any {more}filters, send `no`.")
            more = "more "
            message = await self.bot.wait_for("message", check=check)
            if "no" in message.content.lower():
                if more == '':
                    filters = None
                break
            elif "extension" in message.content.lower():
                await ctx.send(
                    f"You have selected the extension filter. Please tell me whether or not you would like to only show search results from this extension, or to block search results with this extension. Either send the word `accept` or `block`.")
                message = await self.bot.wait_for("message", check=check)
                if "accept" in message.content.lower():
                    await ctx.send(
                        f"You have chosen to only receive results from this extension. Please send the extension that you would like to receive results from.")
                    message = await self.bot.wait_for("message", check=check)
                    if 'true' not in filters:
                        filters['true'] = {}
                    if 'extension' not in filters['true']:
                        filters['true']['extension'] = []
                    filters['true']['extension'].append(
                        "".join([char for char in message.content.lower() if char != "."]))
                elif "block" in message.content.lower():
                    await ctx.send(
                        f"You have chosen to block results from this extension. Please send the extension that you would like to block results from.")
                    message = await self.bot.wait_for("message", check=check)
                    if 'false' not in filters:
                        filters['false'] = {}
                    if 'extension' not in filters['false']:
                        filters['false']['extension'] = []
                    filters['false']['extension'].append(
                        "".join([char for char in message.content.lower() if char != "."]))
            elif "site" in message.content.lower():
                await ctx.send(
                    f"You have selected the site filter. Please tell me whether or not you would like to only show search results from this site, or to block search results from this site. Either send the word `accept` or `block`.")
                message = await self.bot.wait_for("message", check=check)
                if "accept" in message.content.lower():
                    await ctx.send(
                        f"You have chosen to only receive results from this site. Please send the name of the site that you would like to receive results from.")
                    message = await self.bot.wait_for("message", check=check)
                    if 'true' not in filters:
                        filters['true'] = {}
                    if 'site' not in filters['true']:
                        filters['true']['site'] = []
                    filters['true']['site'].append(message.content.lower())
                elif "block" in message.content.lower():
                    await ctx.send(
                        f"You have chosen to block results from this site. Please send the name of the site that you would like to block results from.")
                    message = await self.bot.wait_for("message", check=check)
                    filters['false'] = {} if 'false' not in filters else filters['false']
                    filters['false']['site'] = [] if 'site' not in filters['false'] else filters['false']['site']
                    filters['false']['site'].append(message.content.lower())
        page = f"https://google.com/search?q={article}"
        pageNum = 1
        displayPage = 1
        embed = discord.Embed(title=f"Results for {original}")
        article = await self.request(
            f"{page}&start={(pageNum - 1) * 10}")
        soup = BeautifulSoup(article.content, 'html.parser')
        links = find_all(str(soup), filters)
        breakpage = 0
        while len(list(links.keys())) < 5 and breakpage < 5:
            breakpage += 1
            print("adding")
            pageNum += 1
            additional_article = await self.request(
                f"{page}&start={(pageNum - 1) * 10}")
            additional_soup = BeautifulSoup(additional_article.content, 'html.parser')
            additional_links = find_all(str(additional_soup), filters)
            for key, value in additional_links.items():
                links[key] = value
        print("escaped")
        for key, value in links.items():
            embed.add_field(name=value[0], value=f"[Link]({key})", inline=False)
        embed.set_footer(text=f"Use ⬅️ and ️➡️ to navigate pages | Page {displayPage}")
        message = await ctx.send(embed=embed)
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(m, member):
            return not member.bot and m.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=600.0, check=check)
            except asyncio.TimeoutError:
                break
            if str(reaction) in ["▶️", "▶", "➡️"]:
                pageNum += 1
                displayPage += 1
                await message.remove_reaction(str(reaction), user)
            elif str(reaction) in ["◀️", "️️️◀", "⬅️"]:
                if pageNum > 0:
                    pageNum -= 1
                    displayPage -= 1
            if str(reaction) in ["▶️", "▶", "➡️", "◀️", "️️️◀", "⬅️"]:
                await message.remove_reaction(str(reaction), user)
                if pageNum > 0:
                    article = await self.request(
                        f"{page}&start={(pageNum - 1) * 10}")
                    soup = BeautifulSoup(article.content, 'html.parser')
                    links = find_all(str(soup), filters)
                    embed = discord.Embed(title=f"Results for {original}")
                    while len(list(links.keys())) < 5:
                        print("adding")
                        pageNum += 1
                        additional_article = await self.request(
                            f"{page}&start={(pageNum - 1) * 10}")
                        additional_soup = BeautifulSoup(additional_article.content, 'html.parser')
                        additional_links = find_all(str(additional_soup), filters)
                        print(additional_links)
                        for key, value in additional_links.items():
                            links[key] = value
                    print("escaped")
                    for key, value in links.items():
                        embed.add_field(name=value[0], value=f"[Link]({key})", inline=False)
                    embed.set_footer(
                        text=f"Use ⬅️ and ️➡️ to navigate pages | Page {displayPage}")
                    await message.edit(embed=embed)


    async def embed(self, links, ctx, original):
        if links:
            pass


def setup(bot):
    bot.add_cog(Search(bot))
