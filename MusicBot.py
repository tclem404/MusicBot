import queue
from types import NoneType
import discord
from discord.ext import commands

from dotenv import load_dotenv

import os
import sys
from os import getenv

load_dotenv()

bot = commands.Bot(command_prefix='.')

queue = []
curPlaying = False

@bot.command()
async def join(ctx):
    destination = ctx.author.voice
    bot_channel = ctx.guild.voice_client
    if (bot_channel == None):
        if(destination == None):
            await ctx.reply('I can\'t join a channel you\'re not in silly')
        else:
            await destination.channel.connect()
    else:
        if(destination == None):
            await ctx.reply('I can\'t join a channel you\'re not in buddy')
        elif (destination.channel == bot_channel.channel):
            await ctx.reply('I am already in you channel ya little goober')
        else:
            await destination.channel.connect()

            

@bot.command()
async def play(ctx, link):
    # the voice client =/= channel TY
    destination = ctx.author.voice
    bot_channel = ctx.guild.voice_client

    # if user isn't in a channel
    if(destination == None):
        await ctx.reply('I can\'t join a channel you\'re not in buddy')
        return

    # if bot isn't in a channel / is in a different channel
    if (bot_channel == None or destination.channel != bot_channel.channel):
        await destination.channel.connect()

    if (not curPlaying):
        # if nothing is being played and nothing in queue
        a = 1 + 1
    else:
        # make sure to clean link first
        queue.append(link)

    
        


@bot.command()
async def exit(ctx):
    bot_channel = ctx.guild.voice_client
    aut_channel = ctx.author.voice
    if bot_channel == None:
        await ctx.reply('I am not currently in a voice channel')
    elif (aut_channel == None or aut_channel.channel != bot_channel.channel):
        await ctx.reply('We are not in the same channel')
    else:
        # may need to clean later to make more useful
        # save queue? Answer needed later
        await bot_channel.disconnect()
        
    

bot.run(getenv('TOKEN'))