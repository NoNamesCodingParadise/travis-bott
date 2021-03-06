"""
Initializes the bot and sets up some other things.
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
import utils
import os
from discord import Game, Status, AllowedMentions, Intents
from discord.ext.ipc import Server
from discord.flags import MemberCacheFlags
from utils import MyBot

logger = utils.create_logger("travis-bott", logging.INFO)

my_mentions = AllowedMentions(everyone=False, roles=False)
my_intents = Intents.default()
my_intents.members = True

stuff_to_cache = MemberCacheFlags.from_intents(my_intents)

bot = MyBot(
    status=Status.dnd,
    activity=Game(name="Connecting..."),  # Connecting to the gateway :thonk:
    case_insensitive=True,
    max_messages=1000,
    allowed_mentions=my_mentions,
    intents=my_intents,
    member_cache_flags=stuff_to_cache,
    chunk_guilds_at_startup=False,
)
bot.ipc = Server(bot, "0.0.0.0", 8765, bot.settings["misc"]["secret_key"])

bot.version = "But Better"
bot.description = (
    "A general purpose discord bot that provides a lot of utilities and such to use."
)
bot.owner_ids = {671777334906454026,
                 200301688056315911}

os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"

cogs = [
    "cogs.developer",
    "cogs.meta",
    "cogs.management",
    "cogs.moderation",
    "cogs.fun",
    "cogs.imagemanipulation",
    "cogs.misc",
    "cogs.debug",
    "cogs.beta",
    "cogs.topgg",
    # "cogs.logginglisteners",
    "cogs.utils.help",
    "cogs.utils.errorhandler",
    "cogs.custom.motherrussia",
    "cogs.custom.scrib",
    "cogs.custom.antinuke",
    "cogs.custom.userrequests",
    "jishaku",
]

for cog in cogs:
    try:
        bot.load_extension(cog)
        logger.info(
            f"-> [MODULE] {cog[5:] if cog.startswith('cog') else cog} loaded.")
    except Exception as e:
        logger.critical(f"{type(e).__name__} - {e}")

bot.ipc.start()

if os.name == "nt":
    TOKEN = bot.settings["tokens"]["beta"]
else:
    TOKEN = bot.settings["tokens"]["main"]
bot.run(TOKEN)
