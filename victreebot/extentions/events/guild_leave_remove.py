# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import os

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


async def event_guild_leave_remove(
    event: hikari.GuildLeaveEvent,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    # GUILD GENERAL
    await db.delete_guild(event.guild_id)
    await db.delete_guild_settings(event.guild_id)
    await db.delete_guild_log_settings(event.guild_id)
    await db.delete_guild_stats(event.guild_id)

    # USERS
    await db.delete_guild_users(event.guild_id)

    # LOCATIONS
    await db.delete_guild_locations(event.guild_id)
