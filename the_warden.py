import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import ctypes.util
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Responds to prefixes owo and uwu
bot = commands.Bot(command_prefix=("owo ", "uwu "))


# Sets bot rich presence to "listening to owo help" and prints a login message
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"owo help"))
    print(f"We have logged in as {bot.user}")


# Loads opus, required for voice
if not discord.opus.is_loaded():
    discord.opus.load_opus(ctypes.util.find_library("opus"))
if not discord.opus.is_loaded():
    raise Exception("Opus is stupid, and I am dead")


# Very bad error handling
@bot.event
async def on_command_error(ctx, error):
    description = "Error: "
    if isinstance(error, commands.CommandNotFound):
        description += "That command doesn't exist"
    elif isinstance(error, commands.BotMissingPermissions):
        description += "I don't have the permissions needed to run this command"
    elif isinstance(error, commands.MissingRole):
        description += "You don't have the role(s) needed to use this command"
    elif isinstance(error, commands.BadArgument):
        description += "Unexpected argument (check your capitalization and parameter order)"
    elif isinstance(error, commands.MissingRequiredArgument):
        description += f"Missing required argument: `{error.param}`. If you think you included this, check the order"
    elif isinstance(error, commands.TooManyArguments):
        description += "Too many arguments"
    elif isinstance(error, AttributeError):
        description += "It's probably due to a spelling error somewhere. Please notify Saph#6803"
    elif isinstance(error, commands.CheckFailure):
        description += "You don't have the permissions needed to use this command"
    else:
        print(error)
        await ctx.channel.send("<@363690578950488074>")
        description = "An unexpected error occurred"
    await ctx.channel.send(embed=discord.Embed(description=description,
                                               color=discord.Color.from_rgb(214, 11, 11)))


# Check for bonk and releasing from horny jail
def is_authority():
    async def predicate(ctx):
        return ("Authority Ping" in [r.name for r in ctx.author.roles]) or (ctx.author.id == 586935144959705099)

    return commands.check(predicate)


# Check for banish and release from shadow realm
def can_banish():
    async def predicate(ctx):
        return ctx.author.id in [380550351423537153, 363690578950488074] or "A.S.S." in [r.name for r in
                                                                                         ctx.author.roles]

    return commands.check(predicate)


@bot.command(
    brief="Tells you the latency",
    help="Tells you how long it takes for the bot and discord to communicate in milliseconds. It's the "
         "Discord WebSocket protocol latency, if you know what I mean.")
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000, 2)} ms")


@bot.command(
    brief="Kills the bot. Sophia only",
    help="Do you ever just not feel like connecting to a server, going to terminal, and pressing ctrl c to kill a "
         "process? Well, that's what this command is for.")
async def die(ctx):
    if ctx.author.id == 363690578950488074:
        await ctx.channel.send("Dead. Please wait for <@363690578950488074> to make changes and restart the bot")
        await bot.logout()
    else:
        await ctx.channel.send("Hey, you aren't Sophia!")


@bot.command(
    help="Rickroll"
)
async def imbored(ctx, channel: discord.VoiceChannel = None):
    if channel is None:
        try:
            await ctx.author.voice.channel.connect()
        except AttributeError:
            await ctx.channel.send("You must be in a vc to use this command")
            return
        except discord.errors.ClientException:
            pass
    else:
        await channel.connect()
    vc = get(bot.voice_clients)
    vc.play(discord.FFmpegPCMAudio(executable=""/Users/wyh/ffmpeg"", source="rickroll.mp3"))


@bot.command(
    help="Disconnects from the vc"
)
async def dc(ctx):
    vc = get(bot.voice_clients, guild=ctx.guild)
    await vc.disconnect()


@bot.command(
    brief="Banishes a member to THE SHADOW REALM",
    help="This mysterious command can only be used by Alain.\n""
         "Basically soft-bans people\n""
         ""\n""
         "Examples:\n""
         "owo banish @member\n""
         "Note: you don't have to ping the member, but it's case sensitive")
@can_banish()
async def banish(ctx, member: discord.Member):
    if ctx.author.id in (380550351423537153, 363690578950488074):
        role = get(member.guild.roles, name="Banished")
        if role in member.roles:
            await ctx.channel.send(f"{member} is already in *the shadow realm*")
            return
        await member.add_roles(role)
        await ctx.channel.send(f"Banished {member} to *the shadow realm*")


@bot.command(
    brief="Sends a member to horny jail",
    help="This command can only be used by people with the role `Authority Ping`.\n""
         "It gives a member the `Horny inmate` role, along with a role for the cell that they're assigned to.\n""
         ""\n""
         "Examples:\n""
         "owo bonk @member max (Sends a member to maximum security)\n""
         "owo bonk @member 2 (sends a member to cell 2)\n""
         "owo bonk @member (sends a member to the default cell, cell 1)\n""
         "Note: you don't have to ping the member, but it's case sensitive")
@is_authority()
async def bonk(ctx, member: discord.Member, cell="1", sentence_time="00:30"):
    role1 = get(member.guild.roles, name="Horny inmate")
    times = [int(s) for s in sentence_time.split(":")]
    if role1 in member.roles:
        await ctx.channel.send(f"{member} is already in horny jail")
        return
    elif cell.lower() == "max":
        role2 = get(member.guild.roles, name="MAXIMUM SECURITY HORNY MF")
        await ctx.channel.send(f"Sent {member} to maximum security in horny jail")
    else:
        role2 = get(member.guild.roles, name="Horny Inmate 000" + cell)
        if role2 is None:
            ctx.channel.send("That is not a valid cell number")
            return
        await ctx.channel.send(
            f"Sent {member} to cell {cell} in horny jail for {times[0]} hours and {times[1]} minutes")
    await member.add_roles(role1)
    await member.add_roles(role2)
    try:
        sentence_time = times[0] * 60 * 60 + times[1] * 60
    except IndexError:
        await ctx.channel.send("Please write the period of time using the format hours:minutes, ie 1:15")
        return
    await asyncio.sleep(sentence_time)
    await ctx.invoke(bot.get_command("release"), member=member)


@bot.command(
    brief="Releases someone from the depths",
    help="This command can only be used by people with the role [Authority Ping].\n""
         "It removes all horny jail roles from a member, and also removed the banished role if the person using the "
         "command is Alain.\n"
         "\n"
         "Examples:\n"
         "owo release @member\n"
         "Note: you don't have to ping the member, but it's case sensitive")
@is_authority()
async def release(ctx, member: discord.Member):
    horny_roles = [get(member.guild.roles, name="Horny inmate"), get(member.guild.roles, name="Horny Inmate 0001"),
                   get(member.guild.roles, name="Horny Inmate 0002"), get(member.guild.roles, name="Horny Inmate 0003"),
                   get(member.guild.roles, name="MAXIMUM SECURITY HORNY MF")]
    banish_role = get(member.guild.roles, name="Banished")
    was_in_jail = False
    if ctx.author.id in (380550351423537153, 363690578950488074) and \
            get(member.guild.roles, name="Banished") in member.roles:
        was_in_jail = True
        await member.remove_roles(banish_role)
        await ctx.channel.send(f"Released {member} from *The Shadow Realm*")
    if get(member.guild.roles, name="Horny inmate") in member.roles:
        was_in_jail = True
        await ctx.channel.send(f"Released {member} from horny jail")
    for role in horny_roles:
        await member.remove_roles(role)
    if not was_in_jail:
        await ctx.channel.send(f"There is nothing to release {member} from!")


bot.run("TOKEN")
