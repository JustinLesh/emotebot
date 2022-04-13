import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

#client = discord.Client()

bot = commands.Bot(command_prefix='/')

@bot.command()
async def add(ctx, url, name = None):
    await ctx.channel.send(url + " " + name)

@add.error
async def add_error(ctx, error):
    await ctx.channel.send(error)

# @bot.command()
# async def removeold(ctx, emoji: discord.Emoji):
#     await ctx.channel.send("Deleted the emoji: " + "<:" + emoji.name + ":" + str(emoji.id) + ">")
#     #await emoji.delete()

@bot.command()
async def remove(ctx, emoji: discord.Emoji):
    #msg = await ctx.reply("Deleted the emoji: " + "<:" + emoji.name + ":" + str(emoji.id) + ">")
    msg = await ctx.channel.send("React with ✅ or ❎ to vote to remove the emoji: " + "<:" + emoji.name + ":" + str(emoji.id) + ">", reference=ctx.message)
    await msg.add_reaction("✅")
    await msg.add_reaction("❎")
    #await emoji.delete()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

bot.run(DISCORD_TOKEN)