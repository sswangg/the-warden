import discord, os
from pathlib import Path
from discord.ext import commands
from nudenet import NudeDetector, NudeClassifierLite
from requests import get
from PIL import Image, ImageDraw


class NSFW_censor(commands.Cog):
    """This module auto-censors NSFW. Maybe."""

    def __init__(self, bot):
        self.classifier = NudeClassifierLite()
        self.detector = NudeDetector()
        self.bot = bot
        self.settings = {'Delete NSFW': False, 'Say NSFW Score': False, 'Send Filtered': False}

    async def nsfw_detector(self, classifier=NudeClassifierLite, detector=NudeDetector, message=discord.Message, image_url=str):
        Path(os.path.join(os.getcwd(), 'cache/')).mkdir(parents=True, exist_ok=True)
        filetype = image_url.split('.')[-1]
        filepath = os.path.join(os.getcwd(), f"cache/{hash(image_url)}.{filetype}")
        with open(filepath, 'wb') as file:
            response = get(image_url, headers={'User-Agent': 'Mozilla/5.0'})
            file.write(response.content)

        blacklist_labels = ['EXPOSED_ANUS', 'EXPOSED_BREAST_F', 'COVERED_GENITALIA_F', 'EXPOSED_GENITALIA_F',
                           'EXPOSED_BREAST_M', 'EXPOSED_GENITALIA_M']
        try:
            score = classifier.classify(filepath)[filepath]["unsafe"]
            if self.settings['Say NSFW Score']:
                await message.channel.send(f"NSFW Score: {round(score * 100)}%")
            if score > 0.9 and self.settings['Delete NSFW']:
                await message.delete()
                if self.settings['Send Filtered']:
                    bot = self.bot
                    censor = detector.detect(filepath)
                    if len(censor) > 0:
                        image = Image.open(filepath)
                        censorBlocks = ImageDraw.Draw(image)
                        censorResults = []
                        for censorCoords in censor:
                            if censorCoords['label'] in blacklist_labels:
                                censorBlocks.rectangle(tuple(censorCoords['box']), outline='black', fill='black')
                                censorResults.append(censorCoords['label'] + ' ')
                        image.save(f'./cache/{hash(image_url)}_censored.{filetype}')
                        default_name = bot.user.display_name
                        await bot.user.edit(display_name=message.author.display_name)
                        await message.channel.send(file=discord.File(f'./cache/{hash(image_url)}_censored.{filetype}'))
                        await message.channel.send(f'Censored: {"".join(censorResults)}')

                        await bot.user.edit(display_name=default_name)
                        os.remove(os.path.join(os.getcwd(), f'cache/{hash(image_url)}_censored.{filetype}'))
        except Exception as e:
            await message.channel.send(str(e))
        finally:
            os.remove(filepath)
            return

    @commands.command()
    #@commands.has_role('Authority Ping')
    async def settings(self, ctx, *cmd):
        if cmd:
            cmd = ' '.join(cmd)
            self.settings[cmd] = not self.settings[cmd]
            if not self.settings['Delete NSFW']:
                self.settings['Send Filtered'] = False
            if self.settings['Send Filtered']:
                self.settings['Delete NSFW'] = True
        description = ''
        for num, setting in enumerate(self.settings):
            description += f'[{num+1}] {setting}: '
            if self.settings[setting]:
                description += ':white_check_mark:\n'
            else:
                description += ':x:\n'
        embed = discord.Embed(title='Settings', description=description, color=discord.Color.from_rgb(251, 45, 166))
        embed.set_footer(text='Use owo settings [number] to toggle a setting')
        await ctx.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.bot.user:
            return

        if ctx.attachments and self.settings['Send Filtered'] or self.settings['Delete NSFW']:
            await self.nsfw_detector(detector=self.detector, image_url=ctx.attachments[0].url,
                                     classifier=self.classifier, message=ctx)


def setup(bot):
    bot.add_cog(NSFW_censor(bot))
