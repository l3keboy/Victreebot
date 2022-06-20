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
SUPPORT_SERVER_LINK = os.getenv("SUPPORT_SERVER_LINK")
BOT_INVITE_LINK = os.getenv("BOT_INVITE_LINK")


async def event_guild_join_setup(
    event: hikari.GuildJoinEvent,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    guild = await event.app.rest.fetch_guild(event.guild_id)

    # ADD SERVER TO DATABASE
    await db.insert_guild(guild)
    await db.insert_guild_settings(guild)
    await db.insert_guild_log_settings(guild)
    await db.insert_guild_stats(guild)

    # ADD USERS TO DATABASE
    all_server_members = await event.app.rest.fetch_members(guild)
    for member in all_server_members:
        await db.insert_user(guild, member)
