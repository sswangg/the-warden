import asyncio
import functools
import itertools
import math
import random
from datetime import timedelta

import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ""


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": False,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",
    }

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict):
        super().__init__(source)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.channel = data.get("uploader")
        self.channel_url = data.get("uploader_url")
        self.title = data.get("title")
        self.thumbnail = data.get("thumbnail")
        self.raw_duration = int(data.get("duration"))
        self.duration = self.parse_duration(int(data.get("duration")))
        self.url = data.get("webpage_url")
        self.stream_url = data.get("url")

    def __str__(self):
        return f"**{self.title}** by **{self.channel}**"

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError(f"Couldn't find anything that matches `{search}`")

        if "entries" not in data:
            process_info = data
        else:
            process_info = None
            for entry in data["entries"]:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError(f"Couldn't find anything that matches `{search}`")

        webpage_url = process_info["webpage_url"]
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError(f"Couldn't fetch `{webpage_url}`")

        if "entries" not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info["entries"].pop(0)
                except IndexError:
                    raise YTDLError(f"Couldn't retrieve any matches for `{webpage_url}`")

        return cls(ctx, discord.FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        return str(timedelta(seconds=duration))


class Song:
    __slots__ = ("source", "requester")

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title="Now Playing",
                               description=f"[{self.source.title}]({self.source.url})",
                               color=discord.Color.from_rgb(251, 45, 166))
                 .add_field(name="Channel", value=f"[{self.source.channel}]({self.source.channel_url})")
                 .add_field(name="Song Duration", value=self.source.duration)
                 .set_thumbnail(url=self.source.thumbnail)
                 .set_footer(text=f"Requested by {self.requester}", icon_url=self.requester.avatar_url))
        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(f"Playing :notes: `{self.current.source.title}` - Now!")

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage("This command can\"t be used in DM channels.")

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    @commands.command(brief="Joins a voice channel", invoke_without_subcommand=True)
    async def join(self, ctx: commands.Context):
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(brief="Summons the bot to a voice channel", name="summon")
    @commands.has_permissions(manage_guild=True)
    async def summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        if not channel and not ctx.author.voice:
            raise VoiceError("You are neither connected to a voice channel nor specified a channel to join.")

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(aliases=["disconnect", "dc", "fuck off"],
                      brief="Clears the queue and leaves the voice channel.")
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send("Not connected to any voice channel.")

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(brief="Displays the currently playing song", aliases=["current", "playing"])
    async def now(self, ctx: commands.Context):
        print(ctx.voice_state.voice.position)
        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(brief="Pauses the currently playing song")
    async def pause(self, ctx: commands.Context):
        ctx.voice_state.voice.pause()
        await ctx.send("paused")

    @commands.command(brief="Resumes a currently paused song.")
    async def resume(self, ctx: commands.Context):
        ctx.voice_state.voice.resume()
        await ctx.send("resumed")

    @commands.command(brief="Stops playing song and clears the queue")
    async def clear(self, ctx: commands.Context):
        ctx.voice_state.songs.clear()
        ctx.voice_state.voice.stop()
        await ctx.send("cleared")

    @commands.command(brief="Skip a song")
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_state.is_playing:
            return await ctx.send("Not playing any music right now...")

        ctx.voice_state.skip()
        await ctx.send("skipped")

    @commands.command(brief="Shows the queue")
    async def queue(self, ctx: commands.Context, *, page: int = 1):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ""
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += f"`{i+1}.` [**{song.source.title}**]({song.source.url})\n"

        embed = (discord.Embed(description=f"**{len(ctx.voice_state.songs)} tracks:**\n\n{queue}")
                 .set_footer(text=f"Viewing page {page}/{pages}"))
        await ctx.send(embed=embed)

    @commands.command(brief="Shuffles the queue")
    async def shuffle(self, ctx: commands.Context):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        ctx.voice_state.songs.shuffle()
        await ctx.send("shuffled")

    @commands.command(brief="Removes a song from the queue at a given index.")
    async def remove(self, ctx: commands.Context, index: int):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        await ctx.send(f"Removed {ctx.voice_state.songs[index-1].source.title} from the queue")
        ctx.voice_state.songs.remove(index - 1)

    @commands.command(brief="Loops the currently playing song.")
    async def loop(self, ctx: commands.Context):
        if not ctx.voice_state.is_playing:
            return await ctx.send("Nothing being played at the moment.")

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        if ctx.voice_state.loop:
            await ctx.send("Now looping")
        else:
            await ctx.send("Not looping anymore")

    @commands.command(brief="Plays a song or adds it to the queue")
    async def play(self, ctx: commands.Context, *, search: str):
        """Plays a song.
        If there are songs in the queue, this will be queued until the
        other songs finished playing.
        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self.join)

        await ctx.send(f":musical_note: Searching :mag_right: `{search}`")

        try:
            source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
        except YTDLError as e:
            await ctx.send(f"An error occurred while processing this request: {e}")
        else:
            song = Song(source)
            if len(ctx.voice_state.songs) > 0:
                embed = (discord.Embed(title="Added to queue",
                                       description=f"**[{song.source.title}]({song.source.url})**",
                                       color=discord.Color.from_rgb(251, 45, 166))
                         .add_field(name="Channel", value=f"[{song.source.channel}]({song.source.channel_url})")
                         .add_field(name="Song Duration", value=song.source.duration)
                         .add_field(name="Estimated time until playing",
                                    value=YTDLSource.parse_duration(sum([s.source.raw_duration for s in ctx.voice_state.songs])))
                         .add_field(name="Position in queue", value=len(ctx.voice_state.songs))
                         .set_thumbnail(url=song.source.thumbnail))
                await ctx.send(embed=embed)
            await ctx.voice_state.songs.put(song)

    @join.before_invoke
    @play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("You are not connected to any voice channel.")

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError("Bot is already in a voice channel.")


def setup(bot):
    bot.add_cog(Music(bot))
