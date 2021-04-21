"""
Catches exceptions that are generated by the program or users otherwise.
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

import utils
import discord
import logging
from discord.ext import commands
from utils import MyBot


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: MyBot = bot
        self.logger = utils.create_logger(
            self.__class__.__name__, logging.INFO)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: utils.CustomContext, error: Exception):
        IGNORED_ERRORS = (commands.CommandNotFound,)
        PLAIN_ERRORS = (
            commands.MemberNotFound,
            commands.UserNotFound,
            commands.MissingRequiredArgument,
            commands.BotMissingPermissions,
            commands.CommandOnCooldown,
            commands.NotOwner,
            commands.CheckFailure,
            commands.BadArgument
        )

        if isinstance(error, IGNORED_ERRORS):
            return

        if isinstance(error, PLAIN_ERRORS):
            return await ctx.send(f"{error}")

        await ctx.send(
            "An error occurred, I've logged it to my owner. "
            "You may join the support server to catch up on updates."
        )
        raise error


def setup(bot):
    bot.add_cog(ErrorHandler(bot))