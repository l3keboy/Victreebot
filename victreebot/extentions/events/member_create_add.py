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


async def event_member_create_add(
    event: hikari.MemberCreateEvent,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    guild = await event.app.rest.fetch_guild(event.guild_id)
    # ADD USER
    await db.insert_user(guild, event.user)
