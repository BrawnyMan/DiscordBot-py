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
ROLE_S = os.getenv('ROLE1')
ROLE_P = os.getenv('ROLE2')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

days = ['Pon', 'Tor', 'Sre', 'Cet', 'Pet']
time_offset = 5

with open('urnik.json') as json_file:
    all_schedules = json.load(json_file)

bot = commands.Bot(command_prefix=PREFIX, allowed_mentions=discord.AllowedMentions(everyone=True))
bot.remove_command('help')


def sort_json():
    for role in all_schedules:
        for day in all_schedules[role]:
            x = all_schedules[role][day]
            all_schedules[role][day] = dict(sorted(x.items(), key=lambda y: datetime.datetime.strptime(y[1], "%H:%M")))


def save_json_to_file():
    with open('urnik.json', 'w') as outfile:
        json.dump(all_schedules, outfile)


def is_time(str_time):
    separator = str_time[-3]
    if separator != ':':
        return False
    number = str_time.split(separator)
    if not number[0].isnumeric() and not number[1].isnumeric():
        return False
    if int(number[0]) > 24 or int(number[1]) > 59:
        return False
    return True


async def check_time():
    while True:
        day_of_the_week = datetime.datetime.now().weekday()
        if day_of_the_week not in (5, 6):
            day = days[day_of_the_week]
            current_time = datetime.datetime.now().time()
            # Just to save schedule in json file
            if current_time.hour % 2 == 0 and current_time.minute == 0:
                save_json_to_file()
            for role in all_schedules:
                subjects_in_day = all_schedules[role][day]
                for subject in subjects_in_day:
                    time_of_subject = datetime.datetime.strptime(subjects_in_day[subject], '%H:%M')
                    remind_time = time_of_subject - datetime.timedelta(minutes=time_offset)
                    if remind_time.hour == current_time.hour and remind_time.minute == current_time.minute:
                        embed = discord.Embed(colour=discord.Color.green())
                        embed.add_field(name=subject, value=f'Starts in {time_offset} minutes', inline=False)
                        if role == 'everyone':
                            await bot.get_channel(CHANNEL_ID).send(f'@everyone', embed=embed)
                        else:
                            role_id = ROLE_P if role == 'role2' else ROLE_S
                            await bot.get_channel(CHANNEL_ID).send(f'<@&{role_id}>', embed=embed)
        await asyncio.sleep(60)


@bot.command(name='help')
async def _help(ctx):
    embed = discord.Embed(colour=discord.Color.green())
    embed.set_author(name='Help')
    embed.add_field(name=f'{PREFIX}ping', value='Returns bot respond time in milliseconds', inline=False)
    embed.add_field(name=f'{PREFIX}schedule <opt>', value='Displays schedule, optional opt => schedule for "role1", "role2"',
                    inline=False)
    embed.add_field(name=f'{PREFIX}add [day] [subject] [time]', value=f'Adds to schedule "{PREFIX}add Pon MAT 8:30"',
                    inline=False)
    embed.add_field(name=f'{PREFIX}remove [day] [subject]', value=f'Deletes from schedule "{PREFIX}remove Pon MAT"',
                    inline=False)
    embed.add_field(name=f'{PREFIX}change [day] [subject] [new_time]',
                    value=f'Changes the time of subject "{PREFIX}change Pon MAT 8:30"', inline=False)
    await ctx.send(embed=embed)


# Only two small differences, so it's not worth to write everything again
# There can not be a subject at two different time in on day
async def change_dict(ctx, func, *args):
    if len(args) not in (3, 4):
        return await ctx.send('Wrong arguments, please woof again')
    role = 'everyone'
    if len(args) == 4:
        if args[3] in (<possibilities_for_role1>):
            role = 'role1'
        elif args[3] in (<possibilities_for_role2>):
            role = 'role2'
        else:
            return await ctx.send('Wrong role, please woof again')
    day = args[0].capitalize()
    if day not in days:
        return await ctx.send('Wrong day, please woof again')
    subject = args[1].upper()
    all_subjects = all_schedules[role][day]
    # Difference1
    if func == 'a' and subject in all_subjects:
        return await ctx.send('This subject already exists, please woof again')
    elif func == 'c' and subject not in all_subjects:
        return await ctx.send('This subject does not exists, please woof again')
    # End of difference1
    time = args[2].replace('.', ':')
    if not is_time(time):
        return await ctx.send('Wrong time, please woof again')
    all_schedules[role][day][subject] = time
    # Difference2
    if func == 'a':
        sort_json()
        return await ctx.send('Woof successfully added to schedule')
    if func == 'c':
        sort_json()
        return await ctx.send('Woof schedule successfully changed')
    # End of difference2


@bot.command(name='add')
async def _add(ctx, *args):
    await change_dict(ctx, 'a', *args) # 'a' as add


@bot.command(name='change')
async def _change(ctx, *args):
    await change_dict(ctx, 'c', *args) # 'c' as change


@bot.command(name='remove')
async def _remove(ctx, *args):
    if len(args) not in (2, 3):
        return await ctx.send('Wrong arguments, please woof again')
    role = 'everyone'
    if len(args) == 3:
        if args[2] in (<possibilities_for_role1>):
            role = 'role1'
        elif args[2] in (<possibilities_for_role2>):
            role = 'role2'
        else:
            return await ctx.send('Wrong role, please woof again')
    day = args[0].capitalize()
    if day not in days:
        return await ctx.send('Wrong day, please woof again')
    subject = args[1].upper()
    if subject not in all_schedules[role][day]:
        return await ctx.send('This subject does not exists, please woof again')
    del all_schedules[role][day][subject]
    return await ctx.send('Woof successfully deleted from schedule')


@bot.command(name='schedule')
async def _schedule(ctx, *args):
    arg = args[0].lower() if args else False
    role = 'everyone'
    if arg:
        if arg in (<possibilities_for_role1>):
            role = 'role1'
        elif arg in (<possibilities_for_role2>):
            role = 'role2'
        else:
            return await ctx.send('Wrong argument, please woof again')
    embed = discord.Embed(colour=discord.Color.green())
    embed.set_author(name='Schedule')
    schedule = all_schedules[role]
    for day in schedule:
        classes_in_day = list(schedule[day].items())
        if classes_in_day:
            subjects = [f'{x[0]}: {x[1]}' for x in classes_in_day]
            embed.add_field(name=day, value=', '.join(subjects), inline=False)
    await ctx.send(embed=embed)


@bot.command(name='ping')
async def _ping(ctx):
    await ctx.send(f'Pong! => {round(bot.latency * 1000)}ms')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='with a bone!'))
    print(f'{bot.user.name} has started woofing in Discord!')
    bot.loop.create_task(check_time())


@bot.event
async def on_command_error(ctx, error):
    await ctx.send('Woof Woof I found a problem. Please contact my owner.')
    content = ctx.message.content
    author = ctx.message.author
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await bot.get_user(<your_ID>).send(f'[{time}] {author} ({content})\n{error}')
    

bot.run(TOKEN)
