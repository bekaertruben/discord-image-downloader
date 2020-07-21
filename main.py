import discord
from discord.ext import commands
import os
import requests
import re
from imgur_downloader import ImgurDownloader

TOKEN = '<insert your token here>'

bot = commands.Bot(command_prefix='dl', description='bot description')


async def download_file(url, path, file_name:str=''):
    if not file_name:
        file_name = url.split('/')[-1].split('?')[0] # strip 'filename.png' from 'http://domain.com/something/filename.png?token=L0r3M1p5uM'
    full_path = '{}/{}'.format(path, file_name)

    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.exists(full_path): # this file already exists
        i = 1
        newpath = '{} ({})'.format(full_path, i)
        while os.path.exists(newpath):
            i += 1
            newpath = '{} ({})'.format(full_path, i)
        full_path = newpath
    
    f = open(full_path, 'wb')
    f.write(requests.get(url).content)
    f.close()


@bot.event
async def on_ready():
    print('------')
    print('Image downloader logged in as [{0.user.name} (ID: {0.user.id})]'.format(bot))
    print('------')


@bot.command()
async def channel(ctx, limit:int):
    await ctx.channel.send('downloading all images from last {} messages in channel...'.format(limit))
    foldername = str(ctx.channel.id)
    try:
        async for msg in ctx.channel.history(limit=limit+1):
            if msg.attachments:
                for att in msg.attachments:
                    await download_file(att.url, foldername)
            else:
                temp = re.search('(?P<url>https?://[^\s]+)', msg.content)
                if temp:
                    url = temp.group("url")
                    if re.match('^(https?:\\/\\/)?(\\w+\\.)?imgur.com\\/(\\w*\\d\\w*)+(\\.[a-zA-Z]{3})?$', url): # this is an imgur link
                        ImgurDownloader(url).save_images(foldername) # this is not async, but it'll have to do
                    else:
                        await download_file(url, foldername)
    except:
        await ctx.channel.send('download failed!')
    else:
        await ctx.channel.send('download succeeded!')
    

bot.run(TOKEN)