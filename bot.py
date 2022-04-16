import asyncio
from tkinter import E
from unicodedata import name
import discord
from discord import Embed, Client, Intents
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from PIL import Image
import io
import requests
import os
from dotenv import load_dotenv
 

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


bot = commands.Bot(command_prefix='!')
slash = SlashCommand(bot, sync_commands=True)
guild_id = []
REQUIRED_POSITION = 0
REQUIRED_VOTES = 2
CURRENT_VOTING = []


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    for guild in bot.guilds:
        guild_id.append(guild.id)
        if guild.name == "Cobaltium":
            for role in guild.roles:
                if role.name == "Noble":
                    REQUIRED_POSITION = role.position


@slash.slash(
    name="add",
    description="Provide a url to a BTTV/FFZ emote to add to the server.",
    guild_ids=guild_id,
    options=[
        create_option(
            name="url",
            description="BTTV/FFZ url of the emote to add.",
            required=True,
            option_type=3
        ),
        create_option(
            name="custom_name",
            description="Custom name for the emote to add (if not BTTV/FFZ supplied name).",
            required=False,
            option_type=3
        )
    ]
)
async def _add(ctx:SlashContext, url:str, custom_name:str=None):
    emoji_name = None
    if ctx.author.top_role.position < REQUIRED_POSITION:
        return await ctx.reply("You don't have the permissions to do this. Reason: Role too low.", delete_after=15)
        
    if "betterttv.com/emotes/" in url:
        id = url.split("/")[-1]
        url = "https://cdn.betterttv.net/emote/" + id + "/3x"
        api_url = "https://api.betterttv.net/3/emotes/{}".format(id)
        try:
            r = requests.get(api_url)
            emoji_name = r.json().get("code")
        except:
            return await ctx.reply("The URL you have provided is invalid or BTTV api is down.", delete_after=15)
    elif "frankerfacez.com/emoticon/" in url:
        id = url.split("/")[-1]
        info = id.split("-")
        url = "https://cdn.frankerfacez.com/emoticon/" + info[0] + "/4"
        emoji_name = info[1]
    else:
        return await ctx.reply("The URL you have provided is not the two accepted domains (FFZ or BTTV). URL should start with 'betterttv.com/emotes/' or 'frankerfacez.com/emoticon/'", delete_after=15)
        
    try:
        img = None
        img = requests.get(url).content
        img_bytes = io.BytesIO(img)
        img = Image.open(img_bytes)

        img_size = img_bytes.tell()

        if (img_size > 256 * 1000):
            img.save(img_bytes, quality=20,optimize=True)
        img_bytes.seek(0)
    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
        return await ctx.reply("The URL you have provided is invalid.", delete_after=15)
    try:
        emoji = await ctx.guild.create_custom_emoji(name=emoji_name if custom_name is None else custom_name, image=img_bytes.read())
    except discord.InvalidArgument:
        return await ctx.reply("Invalid image type. Only PNG, JPEG and GIF are supported.", delete_after=15)
    await ctx.reply("Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!".format(emoji, "a" if emoji.animated else ""), delete_after=180)


#[195374504845770762]
@slash.slash(
    name="remove",
    description="Starts a vote to remove an emote from the channel.",
    guild_ids=guild_id
)
async def _remove(ctx:SlashContext, emoji: discord.Emoji):
    if ctx.author.top_role.position < REQUIRED_POSITION:
       return await ctx.reply("You don't have the permissions to do this. Reason: Role too low.", delete_after=15)
        
    if emoji in CURRENT_VOTING:
        return await ctx.reply("Another vote already exists for that emoji. Finish the other vote or delete the previous vote message for that emoji.", delete_after=30)
        
    emote_parts = []
    #check to see if it is a custom emoji
    if emoji[0] == "<" and emoji[-1] == ">":
        #get list of emoji info
        if emoji[1] == "a":     #this means we have an animated emoji
            emoji_parts = emoji[1:-2][1:].split(":")        
            temp = [emoji_parts[0], emoji_parts[1], emoji_parts[2]]
            emoji_parts[0] = temp[emoji_parts[1]]       #emoji_parts[0] is the emoji's name
            emoji_parts[1] = temp[emoji_parts[2]]       #emoji_parts[1] is the emoji's id
            emoji_parts[2] = temp[emoji_parts[0]]       #emoji_parts[2] is the emoji's animated tag
        else:
            emoji_parts = emoji[1:-2][1:].split(":")    #emoji_parts[0] is the emoji's name
            emoji_parts[0] = emoji_parts[0]             #emoji_parts[1] is the emoji's id 

        #fetch emoji from guild's emoji list 
        guild_emoji = discord.utils.get(ctx.guild.emojis, name=emoji_parts[0])

        #if exists in guild then vote to remove otherwise error message.
        if guild_emoji is not None:
            #dont allow them to remove gigachad
            if guild_emoji.name.lower() == "gigachad" or guild_emoji.name.lower() == "chad":
                await ctx.reply("No. " + emoji, allowed_mentions=None, delete_after=15)
            else:
                msg = await ctx.reply("React with ✅ or ❎ to vote to remove the emoji: " + emoji, allowed_mentions=None, delete_after=86400)
                await msg.add_reaction("✅")
                await msg.add_reaction("❎")
                if emoji not in CURRENT_VOTING:
                    CURRENT_VOTING.append(emoji)
        else:
            await ctx.reply(emoji + " is not a valid custom emoji in this server. Try again with a server specific emoji.", allowed_mentions=None, delete_after=15)
    else:
        await ctx.reply(emoji + " is not a valid custom emoji. Try again with a server specific emoji.", allowed_mentions=None, delete_after=15)


@bot.event
async def on_raw_reaction_add(ctx:discord.RawReactionActionEvent):
    channel = bot.get_channel(ctx.channel_id)
    message = await channel.fetch_message(ctx.message_id)
    if message.author == bot.user:
        for r in message.reactions:
            # checks the reactant isn't a bot and the emoji isn't the one they just reacted with
            if ctx.member in await r.users().flatten() and not ctx.member.bot and str(r) != str(ctx.emoji):
                # removes the reaction
                await message.remove_reaction(ctx.emoji, ctx.member)
            elif ctx.member in await r.users().flatten() and not ctx.member.bot and ctx.member.top_role.position < REQUIRED_POSITION:
                await ctx.member.send("You do not have the required permissions to vote.")
                # removes the reaction
                await message.remove_reaction(ctx.emoji, ctx.member)

        #fetch message and then count the votes on the message
        message = await channel.fetch_message(ctx.message_id)
        yea = discord.utils.get(message.reactions, emoji="✅")
        nay = discord.utils.get(message.reactions, emoji="❎")

        #grab the emoji string from the end of the message
        message_contents = message.content
        emoji_start_index = message_contents.find("<")
        emoji_string = message_contents[emoji_start_index:]

        #if the user is reacting to an old vote that the bot started on a previous lifetime - add it so it can be only vote
        if emoji_string not in CURRENT_VOTING:
            CURRENT_VOTING.append(emoji_string)

        #either delete the emoji or delete the message
        if yea.count >= REQUIRED_VOTES:
            emoji_name = emoji_string[1:-2][1:].split(":")[-2]
            emoji = None
            for i in bot.guilds:
                emoji = discord.utils.get(i.emojis, name=emoji_name)
            CURRENT_VOTING.remove(emoji_string)
            await message.delete()
            emoji.delete()
            await channel.send("Vote succeeded to delete " + emoji_string, delete_after=15)    
        elif nay.count >= REQUIRED_VOTES:
            CURRENT_VOTING.remove(emoji_string)
            await message.delete()
            await channel.send("Vote failed to delete " + emoji_string, delete_after=15)


@bot.event
async def on_raw_message_delete(payload:discord.RawMessageDeleteEvent):
    message = payload.cached_message
    if message is not None:
        if message.author == bot.user:
            if "React with ✅ or ❎ to vote to remove the emoji: " in message.content:
                emoji_start_index = message.content.find("<")
                emoji_string = message.content[emoji_start_index:]
                if emoji_string in CURRENT_VOTING:
                    CURRENT_VOTING.remove(emoji_string)


@bot.event
async def on_guild_role_create(role:discord.Role):
    print("role created")
    for guild in bot.guilds:
        if guild.name == "Cobaltium":
            for role in guild.roles:
                if role.name == "Noble":
                    REQUIRED_POSITION = role.position


@bot.event
async def on_guild_role_delete(role:discord.Role):
    print("role deleted")
    for guild in bot.guilds:
        if guild.name == "Cobaltium":
            for role in guild.roles:
                if role.name == "Noble":
                    REQUIRED_POSITION = role.position


@bot.event
async def on_guild_role_update(before:discord.Role, after:discord.Role):
    print("role updated")
    for guild in bot.guilds:
        if guild.name == "Cobaltium":
            for role in guild.roles:
                if role.name == "Noble":
                    REQUIRED_POSITION = role.position


bot.run(DISCORD_TOKEN)