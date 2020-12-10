import os
import discord
import json
import datetime
import asyncio
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX')
ROLE1 = os.getenv('ROLE1')
ROEL2 = os.getenv('ROLE2')
CHANNELID = os.getenv('CHANNEL_ID')
EVERYONE = os.getenv('ROLE_EVERYONE')
days = ['Pon', 'Tor', 'Sre', 'Cet', 'Pet']
time_offset = 5
f = open('urnik.json')
schedulers = json.load(f)
f.close()

bot = commands.Bot(command_prefix=PREFIX)
bot.remove_command('help')


async def check_time():
    while True:
        day_of_the_week = datetime.datetime.now().weekday()
        if day_of_the_week not in (5, 6):
            day = days[day_of_the_week]
            t = datetime.datetime.now().time()
            for schedule in schedulers:
                subjects = schedulers[schedule][day]
                for subject in subjects:
                    s_t = datetime.datetime.strptime(subjects[subject], '%H:%M')
                    subject_time = s_t - datetime.timedelta(minutes=time_offset)
                    if subject_time.hour == t.hour and subject_time.minute == t.minute:
                        embed = discord.Embed(colour=discord.Color.green())
                        embed.add_field(name=subject, value=f'Starts in {time_offset} minutes', inline=False)
                        if schedule == 'everyone':
                            await bot.get_channel(int(CHANNELID)).send(f'@everyone', embed=embed)
                        else:
                            if schedule == 'role1':
                                role_id = ROLE1
                            elif schedule == 'role2':
                                role_id = ROLE2
                            await bot.get_channel(int(CHANNELID)).send(f'<@&{role_id}>', embed=embed)
        await asyncio.sleep(60)


@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(colour=discord.Color.green())
    embed.set_author(name='Help')
    embed.add_field(name='<your_prefix> ping', value='Returns bot respond time in milliseconds', inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def urnik(ctx, *args):
    embed = discord.Embed(colour=discord.Color.green())
    embed.set_author(name='Urnik')
    option = 'everyone'
    if args:
        letter = args[0].lower()
        if letter == '1':
            option = 'role1'
        elif letter == '2':
            option = 'role2'
    for day in schedulers[option]:
        items = list(schedulers[option][day].items())
        u = []
        if items:
            for ure in items:
                u.append(f'{ure[0]} ({ure[1]})')
            embed.add_field(name=day, value=', '.join(u), inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! => {round(bot.latency * 1000)}ms')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='<some_game>'))
    print(f'{bot.user.name} has started working!')
    bot.loop.create_task(check_time())

bot.run(TOKEN)
