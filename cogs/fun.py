"""
Fun cog, provides fun commands to users.
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

import contextlib
import datetime
import logging
import time
import async_cleverbot
import utils
import asyncio
import discord
import typing
import random
import vacefron
from discord.ext import commands, menus

standard_cooldown = 3.0


class EmotionConverter(commands.Converter):
    async def convert(self, ctx: utils.CustomContext, argument: str):
        available_emotions = {
            "neutral": async_cleverbot.Emotion.neutral,
            "sad": async_cleverbot.Emotion.sad,
            "fear": async_cleverbot.Emotion.fear,
            "joy": async_cleverbot.Emotion.joy,
            "anger": async_cleverbot.Emotion.anger,
            "normal": async_cleverbot.Emotion.normal,
            "sadness": async_cleverbot.Emotion.sadness,
            "scared": async_cleverbot.Emotion.scared,
            "happy": async_cleverbot.Emotion.happy,
            "angry": async_cleverbot.Emotion.angry,
        }

        if argument.lower() not in available_emotions.keys():
            raise commands.BadArgument(
                f"Please pick one of these available emotions: {', '.join(available_emotions)}")

        return available_emotions.get(argument)


class RockPaperScissors(menus.Menu):
    def __init__(self, **kwargs):
        kwargs["clear_reactions_after"] = True
        super().__init__(**kwargs)

    def _get_bot_choice(self) -> int:
        """Decides the choice the bot has.
        1 - Rock
        2 - Paper
        3 - Scissors"""

        return random.choice([1, 2, 3])

    def _get_winner(self, author_choice, bot_choice) -> typing.Union[int, str]:
        """Gets the winner of the given match, tie if they're the same."""

        return "tie" if author_choice == bot_choice else (author_choice - bot_choice) % 3

    async def send_initial_message(self,
                                   ctx: utils.CustomContext,
                                   channel: discord.TextChannel) -> discord.Message:
        """Sends the initial message which tells the user to click on a certain reaction."""

        embed = self.bot.embed(ctx)
        embed.description = "Click on Rock, Paper or Scissors and let the council decide your fate."
        return await ctx.send(embed=embed)

    async def _handle_tie(self) -> any:
        embed = self.bot.embed(self.ctx)
        embed.description = "We appeared to have tied... maybe I'll win next time. \N{THINKING FACE}"

        await self.message.edit(embed=embed)
        return self.stop()

    async def _handle_winner(self, winner: int) -> any:
        embed = self.bot.embed(self.ctx)
        if winner == 1:
            embed.description = "Congratulations, I guess - you won! I better get you next time."
        elif winner == 2:
            embed.description = "Congratulations... to me! I win haha!"
        else:
            return await self._handle_tie()

        await self.message.edit(embed=embed)
        return self.stop()

    @menus.button("\U0001faa8")
    async def rock_button(self, payload) -> any:
        player_choice, bot_choice = 1, self._get_bot_choice()
        winner = self._get_winner(player_choice, bot_choice)
        return await self._handle_winner(winner)

    @menus.button("\U0001f4f0")
    async def paper_button(self, payload) -> any:
        player_choice, bot_choice = 2, self._get_bot_choice()
        winner = self._get_winner(player_choice, bot_choice)
        return await self._handle_winner(winner)

    @menus.button("\U00002702")
    async def scissors_button(self, payload) -> any:
        player_choice, bot_choice = 3, self._get_bot_choice()
        winner = self._get_winner(player_choice, bot_choice)
        return await self._handle_winner(winner)


class Fun(commands.Cog, name="fun"):
    """Fun Commands"""

    def __init__(self, bot):
        self.bot: utils.MyBot = bot
        self.show_name = "\N{PARTY POPPER} Fun"
        self.logger = utils.create_logger(
            self.__class__.__name__, logging.INFO)

        self._8ballResponse = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes, definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Signs point to yes",
            "Yes",
            "Reply hazy, try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't bet on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
        ]

        self.all_colours = [
            "darkgreen",
            "purple",
            "orange",
            "yellow",
            "random",
            "black",
            "brown",
            "white",
            "blue",
            "cyan",
            "lime",
            "pink",
            "red",
        ]

    async def handle_cookies(self, user: discord.Member):
        """Handles added cookies to user"""

        sql = (
            "INSERT INTO cookies VALUES($1, $2) "
            "ON CONFLICT (user_id) "
            "DO UPDATE SET cookies = cookies.cookies + 1 "
            "WHERE cookies.user_id = $1;"
        )
        values = (user.id, 1)
        await self.bot.pool.execute(sql, *values)

    @commands.group(name="bottom", invoke_without_command=True)
    async def bottom_group(self, ctx: utils.CustomContext):
        """Base command for all things to do with bottoms."""

        pass

    @bottom_group.command(name="encode")
    async def bottom_encode(self, ctx: utils.CustomContext, *, text: str):
        """Encodes any given text into bottom language."""

        encoded = utils.to_bottom(text)
        if len(encoded) > 1500:
            link = await utils.mystbin(self.bot.session, encoded)
            return await ctx.send(f"That was a little too large for discord to handle... {link}")

        await ctx.send(f"Here you go, filthy bottom:\n{utils.codeblock(encoded)}")

    @bottom_group.command(name="decode")
    async def bottom_decode(self, ctx: utils.CustomContext, *, text: str):
        """Decodes given bottom language text."""
        try:
            decoded = utils.from_bottom(text)
        except Exception as e:
            return await ctx.send(f"{e}")
        if len(decoded) > 1500:
            link = await utils.mystbin(self.bot.session, decoded)
            return await ctx.send(f"That was a little too large for discord to handle... {link}")

        await ctx.send(f"Here you go, filthy bottom:\n{utils.codeblock(decoded)}")

    @commands.command(name="owo-text")
    async def owo_text(self, ctx: utils.CustomContext, *, text: commands.clean_content):
        """Owoifies a given piece of text."""

        owoified = utils.owoify_text(
            text) if not self.bot.config[ctx.guild.id]["owoify"] else text

        await ctx.send(
            owoified,
            allowed_mentions=discord.AllowedMentions.none()
        )

    @commands.command(aliases=["cb"], cooldown_after_parsing=True)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def chatbot(self, ctx: utils.CustomContext, emotion: EmotionConverter = None):
        """Starts an interactive session with the chat bot.
        Type `cancel` to quit talking to the bot."""

        cb = async_cleverbot.Cleverbot(
            self.bot.settings["keys"]["chatbot_api"])
        not_ended = True

        emotion = emotion or async_cleverbot.Emotion.neutral

        await ctx.send("I have started a chat bot session for you, type away! Type `cancel` to end the session.")

        while not_ended:
            try:
                message = await self.bot.wait_for("message",
                                                  timeout=30.0,
                                                  check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            except asyncio.TimeoutError:
                await cb.close()
                not_ended = False
                return await ctx.send("You took a very long time to talk to the bot, so I ended the session.")
            else:
                async with ctx.typing():
                    if message.content.lower() == "cancel":
                        await cb.close()
                        not_ended = False
                        return await ctx.send("Good bye! \N{SLIGHTLY SMILING FACE}")
                    response = await cb.ask(message.content, ctx.author.id, emotion=emotion)

                    try:
                        text = utils.owoify_text(
                            response.text) if self.bot.config[ctx.guild.id]["owoify"] else response.text
                    except (KeyError, AttributeError):
                        text = response.text

                    await message.reply(text)

    @commands.command()
    async def chimprate(self, ctx: utils.CustomContext, user: discord.Member = None):
        """Rate's someones chimpness :monkey:"""

        user = user or ctx.author
        random.seed(user.id)
        chimp_amount = random.randint(0, 100)
        await ctx.send(f"{user.name}'s chimping levels is {chimp_amount}% \N{MONKEY}")

    @commands.command(aliases=["r"])
    async def reddit(self, ctx: utils.CustomContext, subreddit: str):
        """Browse your favourite sub-reddit, gives a random submission from it."""

        async with ctx.typing():
            url = f"https://www.reddit.com/r/{subreddit}/random.json"
            async with self.bot.session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send("That subreddit doesn't exist or something severely wrong just happened.")
                data = await resp.json()
                try:
                    data = data[0]["data"]["children"][0]["data"]
                except KeyError:
                    return await ctx.send("That subreddit doesn't exist or something severely wrong just happened.")

                title, author, ups, downs, score, over_18, url, perma_link, subs, created_at = (
                    data["title"],
                    data["author"],
                    data["ups"],
                    data["downs"],
                    data["score"],
                    data["over_18"],
                    data["url"],
                    data["permalink"],
                    data["subreddit_subscribers"],
                    data["created_utc"]
                )

                if over_18:
                    if not ctx.channel.is_nsfw():
                        return await ctx.send("Bonk! Go to horny jail.")

                embed = self.bot.embed(ctx,
                                       title=title,
                                       url=f"https://www.reddit.com{perma_link}")

                embed.add_field(name="\N{UPWARDS BLACK ARROW}",
                                value=ups)
                embed.add_field(name="\N{DOWNWARDS BLACK ARROW}",
                                value=downs)

                embed.set_image(url=url)
                embed.set_author(name=f"Poster: {author}")
                embed.set_footer(
                    text=f"Subreddit Subs: {subs} | Post score: {score} | Posted at")
                embed.timestamp = datetime.datetime.fromtimestamp(created_at)

                await ctx.send(embed=embed)

    @commands.group(aliases=["cc"], invoke_without_command=True, cooldown_after_parsing=True)
    @commands.cooldown(1, 60, commands.BucketType.member)
    async def cookieclick(self, ctx: utils.CustomContext):
        """First person to click on the cookie wins!"""

        with contextlib.suppress(discord.NotFound):
            timer = 3
            embed = self.bot.embed(
                ctx,
                description="First person to click wins..."
            )

            msg = await ctx.send(embed=embed)

            await asyncio.sleep(3.0)

            for _ in range(timer):
                embed.description = f"Starting in {3 - _} seconds..."
                await msg.edit(embed=embed)

                with contextlib.suppress(discord.Forbidden):
                    await msg.clear_reactions()

                await asyncio.sleep(1)

            embed.description = f"CLICK CLICK CLICK"
            await msg.edit(embed=embed)

            def _check(r, u):
                return all((
                    u != ctx.bot.user,
                    str(r.emoji) == "\N{COOKIE}",
                    not u.bot,
                    r.message.id == msg.id
                ))

            await asyncio.sleep(0.10)

            with contextlib.suppress(discord.Forbidden):
                await msg.clear_reactions()

            start = time.perf_counter()
            try:
                await msg.add_reaction("\N{COOKIE}")
                reaction, user = await self.bot.wait_for("reaction_add", timeout=10.0, check=_check)
            except asyncio.TimeoutError:
                return await ctx.send("Damn, no one wanted the cookie...")

            end = time.perf_counter()

            if end - start <= 0.10:
                return await ctx.send("smh no cheating *tut* *tut* *tut*")

            embed.description = f"{user.mention} got it first in `{end - start:,.2f}` seconds \N{EYES}"
            await msg.edit(embed=embed)
            await self.handle_cookies(user)

    @cookieclick.command(name="leaderboard", aliases=["lb"])
    async def cookieclick_leaderboard(self, ctx: utils.CustomContext):
        """Gives the leaderboard of all cookie clickers."""

        fields = await self.bot.pool.fetch("SELECT * FROM cookies order by cookies DESC LIMIT 100")

        desc = []

        for field in fields:
            user = self.bot.get_user(field["user_id"])
            desc.append(f"{user} - {field['cookies']} cookies")

        source = utils.GeneralPageSource(desc, per_page=10)
        pages = menus.MenuPages(source=source, clear_reactions_after=True)
        await pages.start(ctx)

    @commands.command(aliases=["fban"])
    @commands.cooldown(1, standard_cooldown, commands.BucketType.member)
    async def fakeban(self, ctx: utils.CustomContext, member: discord.Member, *, reason: str = "No Reason Provided."):
        """Fakes banning someone because that's funny, I think."""

        with contextlib.suppress(discord.Forbidden, discord.HTTPException):
            await ctx.message.delete()

        allowed_mentions = discord.AllowedMentions.none()
        await ctx.send(
            f"{member.mention} has been banned by {ctx.author} for: **{reason}**",
            allowed_mentions=allowed_mentions
        )

    @commands.command()
    @commands.cooldown(1, standard_cooldown, commands.BucketType.member)
    async def eject(
        self,
        ctx: utils.CustomContext,
        text: typing.Union[discord.Member, str],
        colour: str,
        confirm: bool = True,
    ):
        """Ejects someone from the game.
        Usage: `{prefix}eject @kal#1806 red True`"""

        vac_api = vacefron.Client()
        text = text.name if type(text) == discord.Member else text

        if colour.lower() not in self.all_colours:
            return await ctx.send(
                f"List of available colours: {', '.join(self.all_colours)}"
            )

        if confirm is not True and confirm is not False:
            return await ctx.send("Confirm must be `true` or `false`")

        image = await vac_api.ejected(text, colour, confirm, confirm)
        image = await image.read(bytesio=True)

        await ctx.send(file=discord.File(image, filename="ejected.png"))
        await vac_api.close()

    @eject.error
    async def on_eject_error(self, ctx: utils.CustomContext, error):
        if isinstance(error, vacefron.BadRequest):
            return await ctx.send(
                f"List of available colours: {', '.join(self.all_colours)}"
            )

    @commands.command(aliases=["rps"])
    @commands.cooldown(1, standard_cooldown, commands.BucketType.member)
    async def rockpaperscissors(self, ctx: utils.CustomContext):
        """Play rock paper scissors with the bot!"""

        game = RockPaperScissors()
        await game.start(ctx)

    @commands.command(aliases=["pp"])
    @commands.cooldown(1, standard_cooldown, commands.BucketType.member)
    async def penis(self, ctx: utils.CustomContext, user: discord.Member = None):
        """Gives you your penis size."""

        user = user or ctx.author
        random.seed(user.id)
        size = 500 if user.id in self.bot.owner_ids else random.randint(0, 100)
        pp = f"8{'=' * size}D"
        await ctx.send(f"eh, that's alright: {pp}")

    @commands.command()
    @commands.cooldown(1, standard_cooldown, commands.BucketType.member)
    async def floof(self, ctx: utils.CustomContext):
        """Get a random image of a cat or dog."""

        url = random.choice(
            ["https://some-random-api.ml/img/dog",
                "https://some-random-api.ml/img/cat"]
        )
        async with self.bot.session.get(url) as r:
            if r.status != 200:
                return await ctx.send(f"The API returned a {r.status} status.")
            data = await r.json()
            image = data["link"]

            embed = self.bot.embed(ctx)
            embed.set_image(url=image)
            await ctx.send(embed=embed)

    @commands.command(aliases=["ye"])
    @commands.cooldown(1, standard_cooldown, commands.BucketType.member)
    async def kanye(self, ctx: utils.CustomContext):
        """Gives a random quote of Kanye West himself."""

        url = "https://api.kanye.rest/"
        async with self.bot.session.get(url) as r:
            if r.status != 200:
                return await ctx.send(f"The API returned a {r.status} status")
            data = await r.json()
            quote = data["quote"]

            embed = self.bot.embed(
                ctx,
                title=f'"{quote}" - Kanye West'
            )
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, standard_cooldown, commands.BucketType.member)
    async def nickme(self, ctx: utils.CustomContext):
        """Gives you a random cool nickname."""

        url = "https://randomuser.me/api/?nat=us,dk,fr,gb,au,ca"
        async with self.bot.session.get(url) as r:
            if r.status != 200:
                return await ctx.send(f"The API returned a {r.status} status.")
            data = await r.json()
            name = data["results"][0]["name"]["first"]

            try:
                await ctx.author.edit(nick=name)
                await ctx.send(f"oo lala, {name} is such a beautiful name for you ???")
            except discord.Forbidden:
                await ctx.send(
                    f"Uhh I couldn't change your name but I chose {name} for you anyways ????"
                )

    @commands.command("8ball", aliases=["8b"])
    @commands.cooldown(1, standard_cooldown, commands.BucketType.member)
    async def _8ball(self, ctx: utils.CustomContext, *, query: str):
        """Ask the oh so magic 8ball a question."""

        await ctx.send(f"???? {ctx.author.mention}, {random.choice(self._8ballResponse)}")

    @commands.command()
    @commands.cooldown(1, standard_cooldown, commands.BucketType.member)
    async def fact(self, ctx: utils.CustomContext):
        """Gives you a cool random fact."""

        url = "https://uselessfacts.jsph.pl/random.json?language=en"
        async with self.bot.session.get(url) as r:
            if r.status != 200:
                return await ctx.send(f"The API returned a {r.status} status")
            data = await r.json()
            fact = data["text"]

            embed = self.bot.embed(
                ctx,
                description=fact
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
