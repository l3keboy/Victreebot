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
        if boss != "egg1" and boss != "egg3" and boss != "egg5" and boss != "eggmega" and boss != "eggshadow":
            success, pokemon, pokemon_image = await bot.validate_pokemon(boss)
            pokemon_name = pokemon.name
        else:
            pokemon_name = boss
        guild_id = result.get("guild_id")
        guild = event.app.cache.get_guild(guild_id) or await event.app.rest.fetch_guild(guild_id)
        end_time = result.get("end_time")
        channel_raids_id = result.get("raid_message_channel_id")
        raid_message_id = result.get("raid_message_id")
        raid_creator_id = result.get("raid_creator_id")
        raid_takes_place_at_to_show = result.get("takes_place_at_to_show")

        instinct_present_list = []
        mystic_present_list = []
        valor_present_list = []
        remote_present_list = []

        instinct_present = result.get("instinct_present")
        if instinct_present is not None:
            if instinct_present.isdigit():
                instinct_present_list.append(int(instinct_present))
            else:
                instinct_present = instinct_present.split(",")
                for instinct in instinct_present:
                    instinct_present_list.append(int(instinct))
        mystic_present = result.get("mystic_present")
        if mystic_present is not None:
            if mystic_present.isdigit():
                mystic_present_list.append(int(mystic_present))
            else:
                mystic_present = mystic_present.split(",")
                for mystic in mystic_present:
                    mystic_present_list.append(int(mystic))
        valor_present = result.get("valor_present")
        if valor_present is not None:
            if valor_present.isdigit():
                valor_present_list.append(int(valor_present))
            else:
                valor_present = valor_present.split(",")
                for valor in valor_present:
                    valor_present_list.append(int(valor))
        remote_present = result.get("remote_present")
        if remote_present is not None:
            if remote_present.isdigit():
                remote_present_list.append(int(remote_present))
            else:
                remote_present = remote_present.split(",")
                for remote in remote_present:
                    remote_present_list.append(int(remote))

        total_attendees = result.get("total_attendees")

        language, auto_delete, *none = await db.get_guild_settings(guild, settings=["language", "auto_delete"])

        RaidClass(
            raid_id,
            raid_type,
            location_type,
            location_name,
            raid_takes_place_at,
            raid_takes_place_at_to_show,
            pokemon_name.lower(),
            guild,
            end_time,
            channel_raids_id,
            raid_message_id,
            raid_creator_id,
            bot,
            bot_aware,
            language,
            auto_delete,
            instinct_present=instinct_present_list if instinct_present_list != [] else None,
            mystic_present=mystic_present_list if mystic_present_list != [] else None,
            valor_present=valor_present_list if valor_present_list != [] else None,
            remote_present=remote_present_list if remote_present_list != [] else None,
            total_attendess=total_attendees,
        )
