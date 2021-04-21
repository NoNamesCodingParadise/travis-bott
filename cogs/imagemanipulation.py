"""
Image manipulation commands.
Copyright (C) 2021 kal-byte

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import asyncdagpi
import discord
import utils
import random
import textwrap
from typing import Optional, Union
from discord.ext import commands
from io import BytesIO
from polaroid import Image as PoImage
from PIL import Image as PImage, ImageFont, ImageDraw
from wand.image import Image as WImage


emoji_user = Optional[Union[discord.Member, discord.PartialEmoji]]

class Manipulation:

    @staticmethod
    @utils.to_thread
    def solarize(b: bytes):
        image = PoImage(b)
        image.solarize()
        save_bytes = image.save_bytes()
        io_bytes = BytesIO(save_bytes)

        return io_bytes

    @staticmethod
    @utils.to_thread
    def brighten(b: bytes, amount: int):
        image = PoImage(b)
        image.brighten(amount)
        save_bytes = image.save_bytes()
        io_bytes = BytesIO(save_bytes)

        return io_bytes

    @staticmethod
    @utils.to_thread
    def facetime(image_one_bytes: bytes,
                 image_two_bytes: bytes):
        image_one = PoImage(image_one_bytes)
        if image_one.size != (1024, 1024):
            image_one.resize(1024, 1024, 5)

        image_two = PoImage(image_two_bytes)
        if image_two.size != (256, 256):
            image_two.resize(256, 256, 5)

        facetime_buttons = PoImage("./data/facetimebuttons.png")
        facetime_buttons.resize(1024, 1024, 5)

        image_one.watermark(image_two, 15, 15)
        image_one.watermark(facetime_buttons, 0, 390)
        io_bytes = BytesIO(image_one.save_bytes())

        return io_bytes

    @staticmethod
    @utils.to_thread
    def magik(image: BytesIO):
        with WImage(file=image) as img:
            img.liquid_rescale(width=int(img.width * 0.5),
                               height=int(img.height * 0.5),
                               delta_x=random.randint(1, 2),
                               rigidity=0)

            img.liquid_rescale(width=int(img.width * 1.5),
                               height=int(img.height * 1.5),
                               delta_x=random.randrange(1, 3),
                               rigidity=0)

            buffer = BytesIO()
            img.save(file=buffer)

        buffer.seek(0)
        return buffer

    @staticmethod
    @utils.to_thread
    def chroma(image: BytesIO):
        with WImage(file=image) as img:
            img.function("sinusoid", [1.5, -45, 0.2, 0.60])
            buffer = BytesIO()
            img.save(file=buffer)

        buffer.seek(0)
        return buffer

    @staticmethod
    @utils.to_thread
    def swirl(image: BytesIO, degrees: int = 90):
        with WImage(file=image) as img:
            degrees = 360 if degrees > 360 else -360 if degrees < -360 else degrees
            img.swirl(degree=degrees)
            buffer = BytesIO()
            img.save(file=buffer)

        buffer.seek(0)
        return buffer

    @staticmethod
    @utils.to_thread
    def alwayshasbeen(txt: str):
        PImage.MAX_IMAGE_PIXELS = (1200 * 1000)

        with PImage.open("./data/ahb.png") as img:
            wrapped = textwrap.wrap(txt, 20)

            font = ImageFont.truetype("./data/JetBrainsMono-Regular.ttf", 36)
            draw = ImageDraw.Draw(img)

            cur_height, pad = 300, 5
            for line in reversed(wrapped):
                w, h = draw.textsize(line, font=font)
                draw.text(((img.width - w) / 2, cur_height), line, font=font)
                cur_height -= h + pad

            buffer = BytesIO()
            img.save(buffer, "png")

        buffer.seek(0)
        return buffer

    @staticmethod
    @utils.to_thread
    def rainbowify(b: bytes):
        img = PoImage(b)
        img.apply_gradient()
        save_bytes = img.save_bytes()
        io_bytes = BytesIO(save_bytes)
        return io_bytes


class ImageManipulation(commands.Cog, name="imagemanipulation"):
    """Image Manipulation"""

    def __init__(self, bot):
        self.bot: utils.MyBot = bot
        self.show_name = "\N{EYE} Image Manipulation"
        self.logger = utils.create_logger(self.__class__.__name__, logging.INFO)

    async def cog_before_invoke(_, ctx: utils.CustomContext):
        await ctx.trigger_typing()

    @staticmethod
    async def get_image(ctx: utils.CustomContext, target: emoji_user):
        if target:
            meth = target.url_as if isinstance(target, discord.PartialEmoji) else target.avatar_url_as
            return await meth(format="png").read()
        if ctx.message.attachments:
            return await ctx.message.attachments[0].read()
        return await ctx.author.avatar_url_as(format="png").read()

    @staticmethod
    async def get_image_url(ctx: utils.CustomContext, target: emoji_user):
        if target:
            meth = target.url_as if isinstance(target, discord.PartialEmoji) else target.avatar_url_as
            return str(meth(format="png"))
        if ctx.message.attachments:
            return await ctx.message.attachments[0].proxy_url
        return str(ctx.author.avatar_url_as(format="png"))

    async def do_dagpi(self, target: emoji_user, feature: asyncdagpi.ImageFeatures):
        feature = getattr(asyncdagpi.ImageFeatures, feature)()
        image = await self.bot.dagpi.image_process(feature, target)
        return discord.File(image.image, f"travis_bott_{feature}.{image.format}")

    @commands.command(aliases=["rainbowify"])
    async def rainbow(self, ctx: utils.CustomContext, *, target: emoji_user):
        """Applies a rainbow effect to a given emoji, attachment or member."""
        image = await self.get_image(ctx, target)
        async with ctx.timeit:
            img = await Manipulation.rainbowify(image)
            file = discord.File(img, "travis_bott_rainbow.png")
            with ctx.embed() as e:
                e.set_image(url="attachment://travis_bott_rainbow.png")
                await ctx.send(file=file, embed=e)

    @commands.command(aliases=["ahb"])
    async def alwayshasbeen(self, ctx: utils.CustomContext, *, text: Optional[str]):
        """It always has been..."""
        text = text or "I'm dumb and didn't put any text..."
        async with ctx.timeit:
            img = await Manipulation.alwayshasbeen(text)
            file = discord.File(img, "travis_bott_ahb.png")
            with ctx.embed() as e:
                e.set_image(url="attachment://travis_bott_ahb.png")
                await ctx.send(file=file, embed=e)

    @commands.command()
    async def swirl(self, ctx: utils.CustomContext, amount: Optional[int], *, target: emoji_user):
        """Swirls a given attachment, emoji or member."""
        image = await self.get_image(ctx, target)
        async with ctx.timeit:
            img = await Manipulation.swirl(BytesIO(image), amount or 90)
            file = discord.File(img, "travis_bott_swirl.png")
            with ctx.embed() as e:
                e.set_image(url="attachment://travis_bott_swirl.png")
                await ctx.send(file=file, embed=e)

    @commands.command(aliases=["chromaify"])
    async def chroma(self, ctx: utils.CustomContext, *, target: emoji_user):
        """Applies a chroma effect to a given emoji, attachment or member."""
        image = await self.get_image(ctx, target)
        async with ctx.timeit:
            img = await Manipulation.chroma(BytesIO(image))
            file = discord.File(img, "travis_bott_chroma.png")
            with ctx.embed() as e:
                e.set_image(url="attachment://travis_bott_chroma.png")
                await ctx.send(file=file, embed=e)

    @commands.command(aliases=["ft"])
    async def facetime(self, ctx: utils.CustomContext, target: emoji_user):
        """Gives a neat facetime effect to a given emoji, attachment or member."""
        image = await self.get_image(ctx, target)
        async with ctx.timeit:
            thumbnail = await ctx.author.avatar_url_as(format="png").read()
            img = await Manipulation.facetime(image, thumbnail)
            file = discord.File(img, "travis_bott_ft.png")
            with ctx.embed() as e:
                e.set_image(url="attachment://travis_bott_ft.png")
                await ctx.send(file=file, embed=e)

    @commands.command()
    async def solarize(self, ctx: utils.CustomContext, *, target: emoji_user):
        """Applies a solarize effect to a given emoji, attachment or member."""
        image = await self.get_image(ctx, target)
        async with ctx.timeit:
            img = await Manipulation.solarize(image)
            file = discord.File(img, "travis_bott_solarize.png")
            with ctx.embed() as e:
                e.set_image(url="attachment://travis_bott_solarize.png")
                await ctx.send(file=file, embed=e)

    @commands.command()
    async def brighten(self, ctx: utils.CustomContext, amount: Optional[int], *, target: emoji_user):
        """Applies a brighten effect to a given emoji, attachment or member."""
        amount = 250 if amount > 250 else amount
        image = await self.get_image(ctx, target)
        async with ctx.timeit:
            img = await Manipulation.brighten(image, amount or 50)
            file = discord.File(img, "travis_bott_brighten.png")
            with ctx.embed() as e:
                e.set_image(url="attachment://travis_bott_brighten.png")
                await ctx.send(file=file, embed=e)

    @commands.command()
    async def wanted(self, ctx: utils.CustomContext, *, target: emoji_user):
        """Puts a given emoji, attachment or member on a wanted poster."""
        image = await self.get_image_url(ctx, target)
        async with ctx.timeit:
            img = await self.do_dagpi(image, "wanted")
            with ctx.embed() as e:
                e.set_image(url=f"attachment://{img.filename}")
                await ctx.send(file=img, embed=e)

    @commands.command(aliases=["colors"])
    async def colours(self, ctx: utils.CustomContext, *, target: emoji_user):
        """Gets the 5 most relevant colours on a given emoji, attachment or member."""
        image = await self.get_image_url(ctx, target)
        async with ctx.timeit:
            img = await self.do_dagpi(image, "colors")
            with ctx.embed() as e:
                e.set_image(url=f"attachment://{img.filename}")
                await ctx.send(file=img, embed=e)

def setup(bot):
    bot.add_cog(ImageManipulation(bot))
