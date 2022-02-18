import queue
from types import NoneType
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer

import asyncio

import youtube_dl

import pafy
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

from dotenv import load_dotenv

import os
import sys
from os import getenv

load_dotenv()

bot = commands.Bot(command_prefix='.')

queueOfSongs = []
curPlaying = False
voice = 0 
wasPlaying = False

@bot.command()
async def join(ctx):
    global voice
    destination = ctx.author.voice
    bot_channel = ctx.guild.voice_client
    if (bot_channel == None):
        if(destination == None):
            await ctx.reply('I can\'t join a channel you\'re not in silly')
        else:
            voice = await destination.channel.connect()
    else:
        if(destination == None):
            await ctx.reply('I can\'t join a channel you\'re not in buddy')
        elif (destination.channel == bot_channel.channel):
            await ctx.reply('I am already in you channel ya little goober')
        else:
            voice = await destination.channel.connect()

            

@bot.command()
async def play(ctx, link):
    # the voice client =/= channel TY
    destination = ctx.author.voice
    bot_channel = ctx.guild.voice_client
    global voice

    # if user isn't in a channel
    if(destination == None):
        await ctx.reply('I can\'t join a channel you\'re not in buddy')
        return

    # if bot isn't in a channel / is in a different channel
    if (bot_channel == None or destination.channel != bot_channel.channel):
        voice = await destination.channel.connect()

    # NEED TO clean link
    global queueOfSongs
    queueOfSongs.append(link)
    print('added to queue')

    global curPlaying
    if (not curPlaying):
        await startPlaying(ctx)

@bot.command()  
async def startPlaying(ctx):
    global queueOfSongs
    global curPlaying
    global voice

    curPlaying = True
    while (len(queueOfSongs) != 0):
        link = queueOfSongs[0]
        queueOfSongs = queueOfSongs[1:len(queueOfSongs)]

        # Youtube Dl Solution - Slow, awkward
        #video_info = youtube_dl.YoutubeDL().extract_info(url = link,download=False )
        #filename = f"song.mp3"
        #options={
        #    'format':'bestaudio/best',
        #    'keepvideo':False,
        #    'outtmpl':filename,
        #}

        #with youtube_dl.YoutubeDL(options) as ydl:
        #    ydl.download([video_info['webpage_url']])

        #await asyncio.sleep(10)
        video = pafy.new(link).getbestaudio()

        source = FFmpegPCMAudio(video.url, **FFMPEG_OPTIONS)
        voice.play(source)
        while(voice.is_playing()):
            await asyncio.sleep(.1)
        
        print('done')
        

    curPlaying = False

@bot.command()
async def quack(ctx):
    global voice
    global curPlaying

    if (ctx.guild.voice_client == None or (ctx.author.voice != None and ctx.author.voice.channel != ctx.guild.voice_client.channel)):
        voice = await ctx.author.voice.channel.connect()
    
    if(not curPlaying):
        curPlaying = True
        source = FFmpegPCMAudio('Duck-quack.mp3')
        voice.play(source)
        while(voice.is_playing()):
            await asyncio.sleep(.1)
        print('done')
        currPlaying = False


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
        # probably not
        await bot_channel.disconnect()

@bot.command()
async def pause(ctx):
    
        
    

bot.run(getenv('TOKEN'))