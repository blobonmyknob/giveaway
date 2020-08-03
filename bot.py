import discord
from discord.ext import commands, menus, tasks
import logging
import random
import json
import os
import string
from datetime import datetime, timedelta


import asyncio

bot = commands.Bot(command_prefix='>')
bot.remove_command('help')


@bot.event
async def on_ready():

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def test(ctx):
    await ctx.send("test ok")

@bot.command(aliases=["раздача"])
async def giveaway(ctx):
    await ctx.send(embed=discord.Embed(color=discord.Color.green(), title = "выберите канал где вы хотите проводить раздачу, к примеру #раздачи"))
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg1 = await bot.wait_for('message', check = check, timeout=30.0)

        channel_converter = discord.ext.commands.TextChannelConverter()
        try:
            channel = await channel_converter.convert(ctx, msg1.content)
        except commands.BadArgument:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "Такого канала не существует,пробуйте заново"))

    except asyncio.TimeoutError:
        await ctx.send("таймоут, напишите команду еще раз")
    if not channel.permissions_for(ctx.guild.me).send_messages or  not channel.permissions_for(ctx.guild.me).add_reactions:
        return await ctx.send(embed=discord.Embed(color=discord.Color.red(), description = f"У меня нет права отправлять сообщение и(или) добавлять реакции(емози) в канале {channel}"))
    await ctx.send(embed=discord.Embed(color=discord.Color.green(), description = f"ок, канал {channel.mention} выбран для раздачи,сколько победителей хотите?(Напишите число)"))
    try:
        msg2 = await bot.wait_for('message', check = check, timeout=30.0)
        try:
            winerscount = int(msg2.content)
        except ValueError:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "Вы не указали число, начните все заново"))

    except asyncio.TimeoutError:
        await ctx.send("таймоут, напишите команду еще раз")

    await ctx.send(embed=discord.Embed(color=discord.Color.green(), title = "Укажите время для giveaway, можете указать к примеру: 20 часов, 4 дня, 5 минут (все через пробел)"))
    try:
        since = await bot.wait_for('message', check = check, timeout=30.0)

    except asyncio.TimeoutError:
        await ctx.send("таймоут, напишите команду еще раз")


    seconds = ("s", "sec", "secs", 'second', "seconds", "c", "сек", "секунда", 'секунду', "секунды", "секунд")
    minutes= ("min", "mins", "minute", "minutes", "мин", "минута", "минуту", 'минуты', 'минут')
    hours= ("h", "hour", "hours", "ч", 'час', 'часа', "часов")
    days = ("d", "day", "days", "д", 'день', 'дня', 'дней')
    weeks = ("w", "week", "weeks", "н", 'нед', 'неделя', "недели", "недель", "неделю")
    months = ("mo", "mos", "month", "months", "мес", "месяц", "месяца", 'месяцев')
    rawsince = since.content
    try:
        time = int(since.content.split(" ")[0])
    except ValueError:
        return await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "вы не указали единицу времени к примеру секунд,минут. Напишите команду заново"))
    since = since.content.split(" ")[1]
    if since.lower() in seconds:
        timewait = time
    elif since.lower() in minutes:
        timewait = time*60
    elif since.lower() in hours:
        timewait = time*3600
    elif since.lower() in days:
        timewait = time*86400
    elif since.lower() in weeks:
        timewait = time*604800
    else:
        return await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "вы не указали единицу времени к примеру секунд,минут. Напишите команду заново"))
    await ctx.send("Укажите приз какой хотите разыграть")
    try:
        msg4 = await bot.wait_for('message', check = check, timeout=30.0)


    except asyncio.TimeoutError:
        await ctx.send("таймоут, напишите команду еще раз")
    await ctx.send(embed = discord.Embed(color=discord.Color.green(), description = f"Приз: {msg4.content}\nколичество победителей: {winerscount}\nканал: {channel.mention}\nчерез {rawsince} "))

    futuredate = datetime.utcnow() + timedelta(seconds=timewait)
    embed1 = discord.Embed(color = discord.Color(random.randint(0x000000, 0xFFFFFF)), title=f"🎉 Новая раздача🎉\n`{msg4.content}`",timestamp = futuredate, description="Добавьте реакцию 🎉 что бы участвовать" )
    embed1.set_footer(text=f"раздача закончится")
    msg = await channel.send(embed=embed1)
    await msg.add_reaction("🎉")
    await asyncio.sleep(timewait)
    message = await channel.fetch_message(msg.id)
    for reaction in message.reactions:
        if str(reaction.emoji) == "🎉":
            users = await reaction.users().flatten()
            if len(users) == 1:
                return await msg.edit(embed=discord.Embed(title="победителей нет"))

    winners = random.sample([user for user in users if not user.bot], k=winerscount)
    await message.clear_reactions()
    emozi='<a:hypertada:677073826265300992>'
    winnerstosend = "\n".join([winner.mention for winner in winners])
    await msg.edit(embed=discord.Embed(title=f"{emozi} победитель {emozi}", description=f"выиграл(и)\n{winnerstosend}",color=discord.Color.blue()).add_field(name=f"приз", value=f"`{msg4.content}`", inline=False))
bot.run(os.environ["TESTBOT"])
