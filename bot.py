import asyncio
from tkinter import E
from unicodedata import name
import discord
from discord import Embed, Client, Intents
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
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

#[195374504845770762]
@slash.slash(
    name="remove",
    description="Starts a vote to remove an emote from the channel.",
    guild_ids=guild_id
)
async def _remove(ctx:SlashContext, emoji: discord.Emoji):
    if ctx.author.top_role.position < REQUIRED_POSITION:
        await ctx.reply("You don't have the permissions to do this. Reason: Role too low.", delete_after=15)
        return
    if emoji in CURRENT_VOTING:
        await ctx.reply("Another vote already exists for that emoji. Finish the other vote or delete the previous vote message for that emoji.", delete_after=30)
        return
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
                await ctx.reply("No. " + emoji, allowed_mentions=None)
            else:
                msg = await ctx.reply("React with ✅ or ❎ to vote to remove the emoji: " + emoji, allowed_mentions=None)
                await msg.add_reaction("✅")
                await msg.add_reaction("❎")
                if emoji not in CURRENT_VOTING:
                    CURRENT_VOTING.append(emoji)
        else:
            await ctx.reply(emoji + " is not a valid custom emoji in this server. Try again with a server specific emoji.", allowed_mentions=None)
    else:
        await ctx.reply(emoji + " is not a valid custom emoji. Try again with a server specific emoji.", allowed_mentions=None)

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
            #emoji.delete()
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