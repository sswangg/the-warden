from discord.ext import commands
import discord
import yaml


class Something(commands.Cog):
    """It's like an anonymous communal google drive. Write whatever you want, do it in DMs for privacy
    (bot logs nothing)"""

    def __init__(self, bot):
        self.bot = bot
        self.documents = {}
        self.bot_color = discord.Color.from_rgb(251, 45, 166)

    @commands.command(
        aliases=['r'],
        brief='Read something in the communal drive thing',
        usage='owo r <title>',
        help='Don\'t feel like writing a help rn')
    async def read(self, ctx, *title):
        title = ' '.join(title)
        with open(r'/warden/The-Warden/thing.yaml') as file:
            self.documents = yaml.full_load(file)
        await ctx.channel.send(embed=discord.Embed(title=title, description=self.documents[title], color=self.bot_color))

    @commands.command(
        aliases=['w'],
        brief='Write something in the communal drive thing',
        usage='owo w `<title>` <text>',
        help='Don\'t feel like writing a help rn')
    async def write(self, ctx, *words):
        useless, title, text = ' '.join(words).split('`')
        self.documents[title] = text[1:]
        with open(r'/warden/The-Warden/thing.yaml', 'w') as file:
            self.documents = yaml.dump(self.documents, file)
        await ctx.channel.send('Written')

    @commands.command(
        brief='List entries in the communal drive thing',
        usage='owo list',
        help='Don\'t feel like writing a help rn')
    async def list(self, ctx):
        with open(r'/warden/The-Warden/thing.yaml') as file:
            self.documents = yaml.full_load(file)
        await ctx.channel.send(embed=discord.Embed(title='Entries', description='\n'.join(self.documents.keys()),
                                                   color=self.bot_color))


def setup(bot):
    bot.add_cog(Something(bot))
