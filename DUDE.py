from datetime import datetime, timedelta
from dotenv import load_dotenv
import numpy as np
import re
import os
import random
import discord

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

class DUDE:
    def __init__(self):
        # see which request is being used
        self.requestInfo = dict()

    # sets up requestInfo for processing later
    def parse(self, sentence):
        self.reset()
        words = [z.lower() for z in re.split('[^a-zA-Z0-9-]', sentence) if len(z) > 0]
        # print(words)
        for c,w in enumerate(words):
            if w == 'play':
                self.requestInfo['play'] = True
            elif w=='help':
                self.requestInfo['help'] = True

    def getRequest(self):
        return self.requestInfo 

    def reply(self):
        #sends multiple replies if necessary
        results = []
        if self.requestInfo['play']:
            results.append("played")
        elif self.requestInfo['help']:
            results.append("help")
        elif self.requestInfo['symbol']:
            results.append("symbol")
        return results

    def reset(self):
        self.requestInfo.clear()
        self.requestInfo['play'] = None
        self.requestInfo['help'] = None


def discordInit(DUDE, DISCORD_TOKEN):
    symbol = '.'
    client = discord.Client()

    @client.event
    async def on_ready():
        print(f'{client.user.name} has connected to Discord!')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{symbol}help"))


    @client.event
    async def on_message(message):
        if message.author == client.user or not message.content:
            return

        command = message.content[0].lower()
        request = message.content[1:].lower()

        if command != f'{symbol}':
            return
            
        embedVar = discord.Embed(color=0x00ff00)
        
        DUDE.parse(request)
        requestInfo = DUDE.getRequest()        
        replies = DUDE.reply()

        if requestInfo['play']:
            ret = "test"
            requestType = "play"
        else:
            ret = helpTemplate(request )
            requestType = "help"
            for k,v in ret.items(): #fix later
                embedVar.add_field(name=k, value=v, inline=True)

        #sending back response
        if any([True for i in requestInfo.values() if isinstance(i, (int, float)) and i == True]):
            if type(ret) == str:
                print(requestType)
                await message.channel.send(ret)
            else:
                embedVar.add_field(name=requestType, value=''.join(ret), inline=False)
                await message.channel.send(embed=embedVar)

    def helpTemplate(request):
        rep = dict()
        req = request.split()
        if len(req) > 1:
            if req[1] == 'play':
                rep['play'] = f'{symbol}play <link_o_video>'
            elif req[1] == 'symbol':
                rep['symbol'] = f'{symbol}symbol <new_symbol>'
        else:
            rep['Supported Commands'] = f'{symbol}help <command>\nplay\nsymbol'
        return rep


    client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    DUDE = DUDE()
    discordInit(DUDE,DISCORD_TOKEN)

