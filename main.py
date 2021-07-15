from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix=('owo ', 'uwu '))
bot.remove_command('help')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'you'))
    print(f'We have logged in as {bot.user}')


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


# Very bad error handling
@bot.event
async def on_command_error(ctx, error):
    description = 'Error: '
    if isinstance(error, commands.CommandNotFound):
        description += 'That command doesn\'t exist'
    elif isinstance(error, commands.BotMissingPermissions):
        description += 'I don\'t have the permissions needed to run this command'
    elif isinstance(error, commands.MissingRole):
        description += 'You don\'t have the role(s) needed to use this command'
    elif isinstance(error, commands.BadArgument):
        description += 'Unexpected argument (check your capitalization and parameter order)'
    elif isinstance(error, commands.MissingRequiredArgument):
        description += f'Missing required argument: `{error.param}`. If you think you included this, check the order'
    elif isinstance(error, commands.TooManyArguments):
        description += 'Too many arguments'
    elif isinstance(error, AttributeError):
        description += 'It\'s probably due to a spelling error somewhere. Please notify Saph#6803'
    elif isinstance(error, commands.CheckFailure):
        description += 'You don\'t have the permissions needed to use this command'
    else:
        print(error)
        await ctx.channel.send("<@363690578950488074>")
        description = 'An unexpected error occurred: '+str(error)
    await ctx.channel.send(embed=discord.Embed(description=description,
                                               color=discord.Color.from_rgb(214, 11, 11)))

#bot.load_extension("cogs.nsfw_detect")
bot.load_extension('cogs.moderation')
bot.load_extension('cogs.other')
bot.load_extension('cogs.write_stuff')
bot.run(TOKEN)
