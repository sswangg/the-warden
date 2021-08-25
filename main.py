from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
import traceback
import sys

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix=("owo ", "uwu "))
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"you"))
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_command_error(ctx, error):
    # Sends an error message
    error_message = {commands.BotMissingPermissions: "I don't have the permissions needed to run this command",
                     commands.MissingRole: "You don't have the role(s) needed to use this command",
                     commands.BadArgument: "Unexpected argument (check your capitalization and parameter order)",
                     commands.MissingRequiredArgument: f"Missing required argument.",
                     commands.TooManyArguments: "Too many arguments",
                     commands.CheckFailure: "You don't have the permissions needed to use this command",
                     AttributeError: "It's probably due to a spelling error somewhere"
                     }
    try:
        description = "Error: " + error_message[error]
    except KeyError:
        if isinstance(error, commands.CommandNotFound):
            return
        description = "An unexpected error occurred: " + str(error)
    await ctx.channel.send(embed=discord.Embed(description=description, color=discord.Color.from_rgb(214, 11, 11)))
    # Logs the error in the errors channel
    error_out = "\n".join(["\\".join(lines.split("\\")[:2] + lines.split("\\")[3:])
                           for lines in str(traceback.format_exc()).split("\n")])
    error_log = "\n".join([
        f"<@!363690578950488074> Error",
        f"```In Channel: {str(ctx.channel)}({ctx.channel.id})",
        f"By User: {str(ctx.author)}({ctx.author.id})",
        f"Command: {ctx.message.content}",
        "\n" f"{str(error)}```"])
    await bot.get_channel(871779186451283968).send(error_log)


@commands.command(hidden=True)
@commands.is_owner()
async def load(module):
    bot.load_extension(module)


@commands.command(hidden=True)
@commands.is_owner()
async def unload(module):
    bot.unload_extension(module)


@commands.command(hidden=True)
@commands.is_owner()
async def reload(module):
    bot.unload_extension(module)
    bot.load_extension(module)


bot.load_extension("cogs.moderation")
bot.load_extension("cogs.other")
bot.run(TOKEN)
