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
from extentions.interactions.raids.RaidClass import RaidClass
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


async def event_started_raid(
    event: hikari.StartedEvent,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    # Raids
    bot_aware.raids = {}

    results = await db.get_all_raids()
    for result in results:
        raid_id = result.get("raid_id")
        raid_id = f"'{raid_id}'"
        raid_type = result.get("raid_type")
        location_type = result.get("location_type")
        location_type = f"'{location_type}'"
        location_name = result.get("location_name")
        location_name = location_name.replace("'", "''")
        location_name = f"'{location_name}'"
        raid_takes_place_at = result.get("takes_place_at")
        boss = result.get("boss")
        success, pokemon, pokemon_image = await bot.validate_pokemon(boss)
        guild_id = result.get("guild_id")
        guild = event.app.cache.get_guild(guild_id) or await event.app.rest.fetch_guild(guild_id)
        end_time = result.get("end_time")
        channel_raids_id = result.get("raid_message_channel_id")
        raid_message_id = result.get("raid_message_id")
        raid_creator_id = result.get("raid_creator_id")

        instinct_present = result.get("instinct_present")
        if instinct_present is not None:
            instinct_present = instinct_present.split(",")
        mystic_present = result.get("mystic_present")
        if mystic_present is not None:
            mystic_present = mystic_present.split(",")
        valor_present = result.get("valor_present")
        if valor_present is not None:
            valor_present = valor_present.split(",")
        remote_present = result.get("remote_present")
        if remote_present is not None:
            remote_present = remote_present.split(",")

        total_attendees = result.get("total_attendees")

        language, auto_delete, *none = await db.get_guild_settings(guild, settings=["language", "auto_delete"])

        RaidClass(
            raid_id,
            raid_type,
            location_type,
            location_name,
            raid_takes_place_at,
            pokemon.name.lower(),
            guild,
            end_time,
            channel_raids_id,
            raid_message_id,
            raid_creator_id,
            bot,
            bot_aware,
            language,
            auto_delete,
            instinct_present=instinct_present,
            mystic_present=mystic_present,
            valor_present=valor_present,
            remote_present=remote_present,
            total_attendess=total_attendees,
        )
