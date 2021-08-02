import asyncio
import ctypes.util
import discord
from discord.ext import commands
from discord.utils import get


class Other(commands.Cog):
    """This and that"""
    def __init__(self, bot):
        self.bot = bot
        self.del_snipes = {}
        self.edit_snipes = {}
        self.bot_color = discord.Color.from_rgb(251, 45, 166)

        # Loads opus, required for voice
        if not discord.opus.is_loaded():
            discord.opus.load_opus(ctypes.util.find_library("opus"))

        @bot.listen("on_message_delete")
        async def on_message_delete(msg):
            """Saves the most recently deleted message in every channel the bot can see"""
            if msg.author.bot:
                return
            self.del_snipes[msg.channel.id] = msg

        @bot.listen("on_message_edit")
        async def on_message_edit(before, after):
            """Saves the most recent message edit in every channel the bot can see"""
            if before.author.bot or before == after:
                return
            self.edit_snipes[before.channel.id] = [before, after]

    def after(self, vc):
        """Makes the bot disconnect from the vc after finishing"""
        coro = vc.disconnect()
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        fut.result()

    @commands.command(
        aliases=["s"],
        help="Gets the most recently deleted message and shows it.",
        brief="Deleted message snipe",
        usage="owo s"
    )
    async def snipe(self, ctx):
        try:
            snipe = self.del_snipes[ctx.channel.id]
        except KeyError:
            return await ctx.send("No snipes in this channel!")
        emb = discord.Embed(color=self.bot_color, description=snipe.content, timestamp=snipe.created_at)
        emb.set_author(name=str(snipe.author), icon_url=snipe.author.avatar_url)
        await ctx.send(embed=emb)

    @commands.command(
        aliases=["editsnipe", "es"],
        help="Gets the most recently edited message and shows that message both before and after the edit.",
        brief="Edit snipe in a channel",
        usage="owo es"
    )
    async def edit_snipe(self, ctx):
        try:
            snipe = self.edit_snipes[ctx.channel.id]
        except KeyError:
            return await ctx.send("No snipes in this channel!")
        emb = discord.Embed(color=self.bot_color, timestamp=snipe[1].created_at)
        emb.add_field(name="Before", value=snipe[0].content, inline=False)
        emb.add_field(name="After", value=snipe[1].content, inline=False)
        emb.set_author(name=str(snipe[0].author), icon_url=snipe[0].author.avatar_url)
        await ctx.send(embed=emb)

    @commands.command(
        help="Joins a vc, plays Never Gonna Give You Up, and disconnects. If a vc isn't specified and the person who"
             "called the command is in a vc, the bot joins that vc.",
        brief="Rickroll",
        usage="owo imbored [vc]"
    )
    async def imbored(self, ctx, channel: discord.VoiceChannel = None):
        if channel is None:
            try:
                await ctx.author.voice.channel.connect()
            except AttributeError:
                await ctx.channel.send("You must be in a vc to use this command")
                return
            except discord.errors.ClientException:
                await ctx.channel.send("The bot is already connected to a vc")
        else:
            await channel.connect()
        vc = get(self.bot.voice_clients)
        vc.play(discord.FFmpegPCMAudio(executable="/usr/local/bin/ffmpeg", source="rickroll.mp3"),
                after=lambda e: self.after(vc))

    @commands.command(
        help="Gives specifics about commands and categories, in an all new ~fancy~ format. Welcome to The Warden 2.0!",
        brief="Gives specifics about commands and categories",
        usage="owo help [command/category]"
    )
    async def help(self, ctx, cmd: str = None):
        if not cmd:
            embed = discord.Embed(
                title="Commands and Categories",
                description="\nUse owo help [command] or owo help [category] to find out more about a specific command "
                            "or category.",
                color=self.bot_color)

            for cog in self.bot.cogs:
                cog = self.bot.get_cog(cog)
                cmds = [c.name for c in cog.get_commands() if not c.hidden]
                if cmds:
                    embed.add_field(
                        name=f"__{cog.qualified_name}__", value=f"`Commands:` {', '.join(cmds)}", inline=True)
            await ctx.send(embed=embed)
        else:
            if command := self.bot.get_command(cmd.lower()):
                command_embed = discord.Embed(title=f"Command: {command.name}",
                                              description=f"**Usage**\n```ini\n{command.usage}```\n"
                                                          f"**Description:**\n```ini\n{command.help}```",
                                              color=self.bot_color)
                command_embed.set_footer(text="<> = required param, [] = optional param")
                return await ctx.send(embed=command_embed)

            for cog in self.bot.cogs:
                if str(cog).lower() == str(cmd).lower():
                    cog = self.bot.get_cog(cog)
                    cog_embed = discord.Embed(title=f"Category: {cog.qualified_name}",
                                              description=f"**Description:**\n```ini\n{cog.description}```",
                                              color=self.bot_color)
                    for c in cog.get_commands():
                        if not c.hidden:
                            cog_embed.add_field(name=f"__{c.name}__", value=c.brief, inline=False)
                    return await ctx.send(embed=cog_embed)
            else:
                await ctx.send("What's that?")

    @commands.command(
        brief="Tells you the latency",
        usage="owo ping",
        help="It tells you the Discord WebSocket protocol latency. In other words, it says how long it takes for the "
             "bot and discord to communicate in milliseconds. IT DOES NOT VARY DEPENDING ON WHO USES THE COMMAND")
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000, 2)} ms")


def setup(bot):
    bot.add_cog(Other(bot))
