from datetime import datetime, timedelta
from discord.ext import commands
from dotenv import load_dotenv
import youtube_dl
import os
import discord



def discordInit(DISCORD_TOKEN):
    symbol = '='
    intents = discord.Intents().all()
    client = discord.Client(intents=intents)
    bot = commands.Bot(command_prefix=symbol,intents=intents)

    youtube_dl.utils.bug_reports_message = lambda: ''
    ytdl_format_options = {
        'format': 'bestaudio/best',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
    }
    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
    class YTDLSource(discord.PCMVolumeTransformer):
        def __init__(self, source, *, data, volume=0.5):
            super().__init__(source, volume)
            self.data = data
            self.title = data.get('title')
            self.url = ""

        @classmethod
        async def from_url(cls, url, *, loop=None, stream=False):
            loop = loop or asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            if 'entries' in data:
                # take first item from a playlist
                data = data['entries'][0]
            filename = data['title'] if stream else ytdl.prepare_filename(data)
            return filename


    @bot.command(name='play', help=f'{symbol} play <song_link>')
    async def play(ctx,url):
        await join(ctx)
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable= f"{os.getcwd()}/ffmpeg/ffmpeg.exe", source=filename))
        await ctx.send(f'**Now playing:** {filename}')

    @bot.command(name='join', help='Bot joins voice channel')
    async def join(ctx):
        if not ctx.message.author.voice:
            await ctx.send(f"{ctx.message.author.name} is not in a voice channel")
            return 
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @bot.command(name='pause', help='Pause the song')
    async def pause(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            return
        await ctx.send("Nothing is playing")

    @bot.command(name='resume', help='Resumes the song')
    async def resume(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            return
        await ctx.send("No songs to resume")

    @bot.command(name='leave', help='Make the bot leave the voice channel')
    async def leave(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            return
        await ctx.send("Not connected to a voice channel")
    
    @bot.command(name='stop', help='Stops the song')
    async def stop(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            return
        await ctx.send("Nothing is playing")

    @bot.event
    async def on_message(message):
       await bot.process_commands(message)

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord!')
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{symbol}help"))

       
    bot.run(DISCORD_TOKEN)

if __name__ == '__main__':
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    discordInit(DISCORD_TOKEN)