import asyncio, discord
from discord.ext import commands

import os, time, html, json, requests
from google_trans_new import google_translator

bot = commands.Bot(command_prefix='!so ')
bot.remove_command('help')

token = os.environ["TOKEN"]


async def bt(games):
    await bot.wait_until_ready()
    while not bot.is_closed():
        for g in games:
            await bot.change_presence(status=discord.Status.online, activity=discord.Game(g))

            await asyncio.sleep(5)


async def getQuestions(q):
    url = "https://api.stackexchange.com/search/advanced?site=stackoverflow.com&q="

    data = requests.get(url + q)
    data = json.loads(data.text)

    try:
        data["items"][0]
    except:
        print("No results found")
        return

    title = []
    link = []

    for i in range(0, 300):
        try:
            title.append(html.unescape(data["items"][i]["title"]))
            link.append(html.unescape(data["items"][i]["link"]))
        except:
            break

    return {'titles': title, 'links': link}


@bot.event
async def on_ready():
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print('------')

    ch = 0
    for g in bot.guilds:
        ch += 1
    await bot.change_presence(status=discord.Status.online, activity=await bt(
        ['!so help ', 'Fighting with the code ', f'Use on {ch} server ', '코드와 사투 ', f'{ch}개의 서버에서 사용 ']))


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="StackoverflowSearcher Help",
                          description="**Commands: **", color=0xD47B1E)
    embed.add_field(name="!so s, !so search", value="**Description**: **Main** command of bot that shows Questions.", inline=False)
    embed.add_field(name="**Example Usage:**",
                    value="!so s 파이썬 포스트\n!so search 파이썬 포스트\n- Search after translation into English\n- Supports almost all languages",
                    inline=False)
    try:
        await ctx.author.send(embed=embed)
    except:
        await ctx.send(
            f"<@{ctx.author.id}>, Direct mail transmission failed. You have blocked the bot or check your privacy settings.")
    else:
        await ctx.send(f"<@{ctx.author.id}>, I sent a direct message")


@bot.command()
async def ping(ctx):
    await ctx.message.delete()

    before = time.monotonic()
    message = await ctx.send("Pong!")
    ping = (time.monotonic() - before) * 1000
    await message.edit(content=f"Pong!  `{int(ping)}ms`")
    print(f'Ping {int(ping)}ms')


@bot.command()
async def s(ctx):
    q = ctx.message.content[6:]

    if not q:
        await ctx.send(f"<@{ctx.author.id}>, You entered the wrong command. Learn how to use it with `!so help`")
        return

    translator = google_translator()

    if not str(q).encode().isalpha():
        q = translator.translate(str(q), lang_tgt="en")

    result = await getQuestions(q)

    if not result:
        await ctx.send(f"<@{ctx.author.id}>, No results found")
        return

    if ((int) (len(result["titles"]))) < 5:
        pages = 1
    else:
        pages = (int) (len(result["titles"]) / 5)

    embed = []

    for i in range(pages):
        embed.append(discord.Embed(title="Stackoverflow Questions",
                                   description=f"**Search Word: {q}**\n**Page: " + str(i + 1) + "/" + str(pages) + "**", color=0xD47B1E))

    for i in range(pages):
        for j in range(i * 5, i * 5 + 5):
            try:
                embed[i].add_field(name="\u200b", value=f"[{str(result['titles'][j])}]({str(result['links'][j])})",
                                   inline=False)
            except:
                break

    cur_page = 1

    message = await ctx.send(embed=embed[cur_page - 1])
    # getting the message object for editing and reacting

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=None, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(embed=embed[cur_page - 1])
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(embed=embed[cur_page - 1])
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds


@bot.command()
async def search(ctx):
    q = ctx.message.content[10:]

    if not q:
        await ctx.send(f"<@{ctx.author.id}>, You entered the wrong command. Learn how to use it with `!so help`")
        return

    translator = google_translator()

    if not str(q).encode().isalpha():
        q = translator.translate(str(q), lang_tgt="en")

    result = await getQuestions(q)

    if not result:
        await ctx.send(f"<@{ctx.author.id}>, No results found")
        return

    if ((int) (len(result["titles"]))) < 5:
        pages = 1
    else:
        pages = (int) (len(result["titles"]) / 5)

    embed = []

    for i in range(pages):
        embed.append(discord.Embed(title="Stackoverflow Questions",
                                   description=f"**Search Word: {q}**\n**Page: " + str(i + 1) + "/" + str(pages) + "**", color=0xD47B1E))

    for i in range(pages):
        for j in range(i * 5, i * 5 + 5):
            try:
                embed[i].add_field(name="\u200b", value=f"[{str(result['titles'][j])}]({str(result['links'][j])})",
                                   inline=False)
            except:
                break

    cur_page = 1

    message = await ctx.send(embed=embed[cur_page - 1])
    # getting the message object for editing and reacting

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=None, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(embed=embed[cur_page - 1])
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(embed=embed[cur_page - 1])
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds

bot.run(token)
