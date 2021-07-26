from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix=("owo ", "uwu "))
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"you"))
    print(f"We have logged in as {bot.user}")


# Abandoned idea for making the bot able to join other servers
@bot.event
async def on_guild_join(guild):
    general = guild.system_channel
    embed = discord.Embed(
        title="Hello!",
        description=f"Thanks for adding me to {guild.name}! Any user with the perm `Ban Members` can use `owo setup` "
                    f"in any channel to begin the process of setting up this bot",
        color=bot.user.color
    )
    await general.send(embed=embed)

"""
# Very bad error handling
# Update: Slightly less bad error handling
@bot.event
async def on_command_error(ctx, error):
    error_message = {commands.CommandNotFound: "That command doesn't exist",
                     commands.BotMissingPermissions: "I don't have the permissions needed to run this command",
                     commands.MissingRole: "You don't have the role(s) needed to use this command",
                     commands.BadArgument: "Unexpected argument (check your capitalization and parameter order)",
                     commands.MissingRequiredArgument: f"Missing required argument.",
                     commands.TooManyArguments: "Too many arguments",
                     commands.CheckFailure: "You don't have the permissions needed to use this command",
                     AttributeError: "It's probably due to a spelling error somewhere. Please notify Saph#6803"
                     }
    try:
        description = "Error: " + error_message[error]
    except KeyError:
        print(error)
        await ctx.channel.send("<@363690578950488074>")
        description = "An unexpected error occurred: " + str(error)
    await ctx.channel.send(embed=discord.Embed(description=description, color=discord.Color.from_rgb(214, 11, 11)))
"""

# bot.load_extension("cogs.nsfw_detect")
bot.load_extension("cogs.moderation")
bot.load_extension("cogs.other")
bot.run(TOKEN)
