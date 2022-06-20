# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import os
import time

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from extentions.interactions.raids.RaidClass import RaidClass
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


async def event_raw_reaction_add_raid(
    event: hikari.GuildReactionAddEvent,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    raid: RaidClass
    if event.member.is_bot:
        return

    guild = event.app.cache.get_guild(event.guild_id) or await event.app.rest.fetch_guild(event.guild_id)
    instinct_emoji_id, mystic_emoji_id, valor_emoji_id, raid_timeout, *none = await db.get_guild_settings(
        guild, settings=["instinct_emoji_id", "mystic_emoji_id", "valor_emoji_id", "raid_timeout"]
    )

    message = event.app.cache.get_message(event.message_id) or await event.app.rest.fetch_message(
        event.channel_id, event.message_id
    )
    raid_id, *none = await db.get_raid_details_by_message(message, guild, details=["raid_id"])
    raid = bot_aware.raids.get(f"'{raid_id}'")

    if event.emoji_id == instinct_emoji_id:
        if raid.end_time - time.time() > int(raid_timeout):
            await raid.update_raid_from_reaction("instinct", True, event.member)
        else:
            emoji = event.app.cache.get_emoji(instinct_emoji_id) or await event.app.rest.fetch_emoji(
                guild, instinct_emoji_id
            )
            await message.remove_reaction(emoji, user=event.member)
    if event.emoji_id == mystic_emoji_id:
        if raid.end_time - time.time() > int(raid_timeout):
            await raid.update_raid_from_reaction("mystic", True, event.member)
        else:
            emoji = event.app.cache.get_emoji(mystic_emoji_id) or await event.app.rest.fetch_emoji(
                guild, mystic_emoji_id
            )
            await message.remove_reaction(emoji, user=event.member)
    if event.emoji_id == valor_emoji_id:
        if raid.end_time - time.time() > int(raid_timeout):
            await raid.update_raid_from_reaction("valor", True, event.member)
        else:
            emoji = event.app.cache.get_emoji(valor_emoji_id) or await event.app.rest.fetch_emoji(guild, valor_emoji_id)
            await message.remove_reaction(emoji, user=event.member)
    if event.emoji_name == "1️⃣":
        if raid.end_time - time.time() > int(raid_timeout):
            await raid.update_raid_from_reaction("one", True, event.member)
        else:
            await message.remove_reaction("1️⃣", user=event.member)
    if event.emoji_name == "2️⃣":
        if raid.end_time - time.time() > int(raid_timeout):
            await raid.update_raid_from_reaction("two", True, event.member)
        else:
            await message.remove_reaction("2️⃣", user=event.member)
    if event.emoji_name == "3️⃣":
        if raid.end_time - time.time() > int(raid_timeout):
            await raid.update_raid_from_reaction("three", True, event.member)
        else:
            await message.remove_reaction("3️⃣", user=event.member)
    if event.emoji_name == "🇷":
        if raid.end_time - time.time() > int(raid_timeout):
            await raid.update_raid_from_reaction("remote", True, event.member)
        else:
            await message.remove_reaction("🇷", user=event.member)
