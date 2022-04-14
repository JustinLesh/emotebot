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

bot.run(DISCORD_TOKEN)