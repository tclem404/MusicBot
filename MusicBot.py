from types import NoneType
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer

import asyncio

import pafy
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

import validators

from urllib.request import urlopen

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
skipped = False
looping = False
paused = False

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
async def play(ctx, *link):
    # the voice client =/= channel TY
    destination = ctx.author.voice
    bot_channel = ctx.guild.voice_client
    global voice

    searchUrl = ''
    # if user isn't in a channel
    if(destination == None):
        await ctx.reply('I can\'t join a channel you\'re not in buddy')
        return

    # if bot isn't in a channel / is in a different channel
    if (bot_channel == None or destination.channel != bot_channel.channel):
        voice = await destination.channel.connect()

    # NEED TO clean link
    global queueOfSongs
    validLink = False
    if (len(link) == 1):
        try:
            # what to do if it is a youtube link
            validators.url(link[0])
            if not ('youtu' in link[0].lower()):
                await ctx.reply('Sorry, only youtube links work')
                return
            validLink = True
            queueOfSongs.append(link[0])
        except:
            # validators throws an execption so this is just to catch it incase
            a = 1 + 1
    
    if (not validLink):
        # assuming to be non link, but rather a youtube search
        search = 'https://www.youtube.com/results?search_query=' + '+'.join(link)
        page = urlopen(search)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")

        place = html.find('videoId')
        html = html[place+10:]
        searchUrl = 'https://www.youtube.com/watch?v=' + html[0:html.find("\"")]
        queueOfSongs.append(searchUrl)

    if len(queueOfSongs) == 1:
        await ctx.reply('Now Playing ' + searchUrl)
    else:
        await ctx.reply('Added to the queue')

    global curPlaying
    if (not curPlaying):
        await startPlaying(ctx)

@bot.command()  
async def startPlaying(ctx):
    global queueOfSongs
    global curPlaying
    global voice
    global wasPlaying
    global paused

    curPlaying = True
    if (not wasPlaying):
        await initPlayLoop(ctx)
    else:
        paused = False
        await initPlayLoop(ctx)
    
    curPlaying = False

async def initPlayLoop(ctx):
    global queueOfSongs
    global wasPlaying
    global voice
    global skipped
    global curPlaying
    global paused
    while (len(queueOfSongs) != 0 or wasPlaying) and not paused:
        if wasPlaying:
            voice.resume()
            wasPlaying = False
        else:
            link = queueOfSongs[0]

            video = pafy.new(link).getbestaudio()

            # not my solution, got from internet: https://stackoverflow.com/questions/66115216/discord-py-play-audio-from-url
            source = FFmpegPCMAudio(video.url, **FFMPEG_OPTIONS)
            voice.play(source)
        
        while(voice.is_playing()):
            await asyncio.sleep(.1)
            
        if not looping:
            queueOfSongs = queueOfSongs[1:len(queueOfSongs)]

@bot.command()
async def loop(ctx):
    global looping
    looping = not looping
    if (looping):
        await ctx.reply('Now Looping')
    else:
        await ctx.reply('No Longer Looping')

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
        curPlaying = False


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
    global curPlaying
    global wasPlaying
    global voice
    global paused
    if (curPlaying):
        curPlaying = False
        wasPlaying = True
        paused = True
        voice.pause()

@bot.command()
async def skip(ctx):
    await ctx.reply('Skipping...')
    # ends while statement in playLoop
    voice.pause()

@bot.command()
async def queue(ctx):
    global queueOfSongs
    if (len(queueOfSongs) == 0):
        ctx.reply('No Songs in Queue')
    else:
        msg = 'Now Playing: ' + pafy.new(queueOfSongs[0]).title
        for i in range(1,5):
            if (i >= len(queueOfSongs)):
                break
            else:
                msg = msg + '\n' + str(i) + ': ' + pafy.new(queueOfSongs[i]).title
        if (len(queueOfSongs) > 5):
            msg = msg + '\nAnd ' + str(len(queueOfSongs) - 5) + ' more'
        await ctx.reply(msg)


bot.run(getenv('TOKEN'))