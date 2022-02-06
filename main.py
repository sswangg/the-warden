import os
import traceback

import discord
from discord.ext import commands
from dotenv import load_dotenv

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
        # Logs the error in the errors channel
        error_log = "\n".join([
            f"<@!363690578950488074> Error",
            f"```In Channel: {str(ctx.channel)}({ctx.channel.id})",
            f"By User: {str(ctx.author)}({ctx.author.id})",
            f"Command: {ctx.message.content}",
            "\n"+"".join(traceback.format_exception(type(error), error, error.__traceback__))+"```"])
        await bot.get_channel(871779186451283968).send(error_log)
    await ctx.channel.send(embed=discord.Embed(description=description, color=discord.Color.from_rgb(214, 11, 11)))


@bot.command(hidden=True)
@commands.is_owner()
async def kill(ctx):
    await ctx.channel.send("Terminating")
    await bot.close()


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, module):
    bot.load_extension(module)
    await ctx.channel.send(f"Loaded {module}")


@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, module):
    bot.unload_extension(module)
    await ctx.channel.send(f"Unloaded {module}")


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, module):
    bot.reload_extension(module)
    await ctx.channel.send(f"Reloaded {module}")


bot.load_extension("cogs.moderation")
bot.load_extension("cogs.other")
bot.run(TOKEN)
