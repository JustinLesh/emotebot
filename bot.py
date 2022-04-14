import asyncio
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
REQUIRED_POSITION = 8

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    for guild in bot.guilds:
        guild_id.append(guild.id)


@slash.slash(
    name="remove",
    description="Starts a vote to remove an emote from the channel.",
    guild_ids=[195374504845770762]
)
async def _remove(ctx:SlashContext, emoji: discord.Emoji):
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
        else:
            await ctx.reply(emoji + " is not a valid custom emoji in this server. Try again with a server specific emoji.", allowed_mentions=None)
    else:
        await ctx.reply(emoji + " is not a valid custom emoji. Try again with a server specific emoji.", allowed_mentions=None)

@bot.event
async def on_raw_reaction_add(ctx:discord.RawReactionActionEvent):
    channel = bot.get_channel(ctx.channel_id)
    message = await channel.fetch_message(ctx.message_id)
    if message.author == bot.user:
        yay_count = 0
        nay_count = 0
        for r in message.reactions:
            # checks the reactant isn't a bot and the emoji isn't the one they just reacted with
            if ctx.member in await r.users().flatten() and not ctx.member.bot and str(r) != str(ctx.emoji):
                # removes the reaction
                await message.remove_reaction(ctx.emoji, ctx.member)
            elif ctx.member in await r.users().flatten() and not ctx.member.bot and ctx.member.top_role.position < REQUIRED_POSITION:
                await ctx.member.send("You do not have the required permissions to vote.")
                # removes the reaction
                await message.remove_reaction(ctx.emoji, ctx.member)

        message = await channel.fetch_message(ctx.message_id)
        yay = discord.utils.get(message.reactions, emoji="✅")
        nay = discord.utils.get(message.reactions, emoji="❎")
        

#noble is position 8 in roles

bot.run(DISCORD_TOKEN)