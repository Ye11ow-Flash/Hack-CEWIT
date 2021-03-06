# bot.py
# 02.18.2022
from discord.ext import commands
from dotenv import load_dotenv
import discord
import os
import json
import random
import requests
import asyncio
import major_scrapper, courses_scrapper, planner, degreeinfo_scrapper

intents = discord.Intents.all()
load_dotenv()
TOKEN = os.environ.get('TOKEN', 3)

bot = commands.Bot(command_prefix="-", intents=intents)
bot.remove_command('help')

random.seed(0)

def create_embed(query_dict):
    embed = discord.Embed(
        title=query_dict["title"], description=query_dict["description"], colour=0X650100)
    embed.add_field(name="Prerequisites",
                    value=query_dict["prereq"], inline=False)
    embed.add_field(name="Credits",
                    value=query_dict["credits"], inline=False)
    embed.add_field(name="Course Code",
                    value=query_dict["code"], inline=False)
    return embed

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.command()
async def degreeinfo(ctx, major):
    description = degreeinfo_scrapper.get_degree_info(major)[0]
    embed = discord.Embed(title=major.upper(), description=description, colour=0X650100)
    await ctx.send(embed=embed)

@bot.command()
async def courseinfo(ctx, subject, code):
    all_courses = major_scrapper.get_course_data(subject, code)
    embed = create_embed(all_courses)
    await ctx.send(embed=embed)

@bot.command()
async def randomcourse(ctx, major):
    course_lists = courses_scrapper.get_courses(major)
    randomNum = random.randint(0, len(course_lists)-1)
    random_course_code = course_lists[randomNum]['code']
    course_info_dict = major_scrapper.get_course_data(major, random_course_code)
    embed = create_embed(course_info_dict)
    await ctx.send(embed=embed)

@bot.command()
async def listcourse(ctx, major):
    return_string = "```\n"
    all_courses = courses_scrapper.get_courses(major)
    for i in all_courses:
        j = i['code'] + i['title'] + "\n"
        return_string += j
        if (len(return_string + j) * 2 >= 2000):
            await ctx.send(return_string + f"```")
            return_string = "```\n"
    await ctx.send(return_string + '\n```')

@bot.command(name="add")
async def add_class(ctx, course, code, semester, year):
    time = semester + year
    planner.add_course(str(ctx.author.id), course, code, time)
    await ctx.reply(f"Added {course} {code} to {semester} {year}")
    
@bot.command(name='remove')
async def remove_class(ctx, course, code):
    await ctx.reply(planner.remove_course(str(ctx.author.id), course, code))
    
@bot.command(name='move')
async def move_class(ctx, course, code, oldsem, oldyear, newsem, newyear):
    old = oldsem + oldyear
    new = newsem + newyear
    await ctx.reply(planner.move_course(str(ctx.author.id), course, code, old, new))

@bot.command(name='plan')
async def plans(ctx):
    await ctx.send(planner.planner(str(ctx.author.id)))

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help", description="Accessing the undergrad bulletin has never been easier! A major code is the 3 digit major classification, such as CSE or CHE", colour=0X650100)
    embed.add_field(name="-help",
                    value="list of all commands", inline=False)
    embed.add_field(name="-courseinfo  <majorcode> <number>",
                    value="information for any course", inline=False)
    embed.add_field(name="-listcourse  <majorcode>",
                    value="lists all courses for <major>", inline=False)
    embed.add_field(name="-degreeinfo <majorcode>",
                    value="information about degree requirements", inline=False)
    embed.add_field(name="-randomcourse <majorname>",
                    value="random course in that major!", inline=False)
    embed.add_field(name="-add <majorcode> <number> <semester> <year>",
                value="Add a course to your planner!", inline=False)
    embed.add_field(name="-remove <majorcode> <number>",
                value="Remove a course from your planner!", inline=False)
    embed.add_field(name="-move <majorcode> <number> <old semester> <old year> <new semester> <new year>",
                value="Move a course in your planner!", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send("Sorry! I encountered this error: \n```" + f"{error}" + '```')

bot.run(TOKEN)
