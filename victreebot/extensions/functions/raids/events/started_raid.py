# Copyright (c) 2022-present l3keboy

import hikari
import lightbulb

from victreebot.core.bot import Bot
from victreebot.utils.classes.RaidClass import RaidClass

loader = lightbulb.Loader()


@loader.listener(hikari.StartedEvent)
async def started_raid(_event: hikari.StartedEvent, bot: Bot) -> None:
    """Event to readd existing raid to bot raids in memory."""
    all_raids = await bot.database.get_all_raids()
    for raid in all_raids:
        guild_settings = await bot.database.get_guild_settings(raid.guild_id)
        if guild_settings is None:
            return

        boss = raid.boss
        if boss not in {"egg1", "egg3", "egg5", "eggmega", "eggshadow"}:
            success, pokemon, _ = await bot.utils.validate_pokemon(boss)
            if not success or not pokemon:
                return
            pokemon_name = pokemon.name
        else:
            pokemon_name = boss

        instinct_present_list: list[int] = []
        mystic_present_list: list[int] = []
        valor_present_list: list[int] = []
        remote_present_list: list[int] = []

        instinct_present = raid.instinct_present
        if instinct_present is not None:
            if instinct_present.isdigit():
                instinct_present_list.append(int(instinct_present))
            else:
                instinct_present = instinct_present.split(",")
                instinct_present_list.extend(int(instinct) for instinct in instinct_present)
        mystic_present = raid.mystic_present
        if mystic_present is not None:
            if mystic_present.isdigit():
                mystic_present_list.append(int(mystic_present))
            else:
                mystic_present = mystic_present.split(",")
                mystic_present_list.extend(int(mystic) for mystic in mystic_present)
        valor_present = raid.valor_present
        if valor_present is not None:
            if valor_present.isdigit():
                valor_present_list.append(int(valor_present))
            else:
                valor_present = valor_present.split(",")
                valor_present_list.extend(int(valor) for valor in valor_present)
        remote_present = raid.remote_present
        if remote_present is not None:
            if remote_present.isdigit():
                remote_present_list.append(int(remote_present))
            else:
                remote_present = remote_present.split(",")
                remote_present_list.extend(int(remote) for remote in remote_present)

        RaidClass(
            raid.raid_id,
            raid.raid_type,
            raid.location_type,
            raid.location_name,
            raid.takes_place_at,
            raid.takes_place_at_to_show,
            pokemon_name.lower(),
            raid.guild_id,
            int(raid.end_time),
            raid.raid_message_channel_id,
            raid.raid_message_id,
            raid.raid_creator_id,
            bot,
            guild_settings.language,
            guild_settings.auto_delete,
            instinct_present=instinct_present_list if instinct_present_list != [] else None,
            mystic_present=mystic_present_list if mystic_present_list != [] else None,
            valor_present=valor_present_list if valor_present_list != [] else None,
            remote_present=remote_present_list if remote_present_list != [] else None,
            total_attendess=raid.total_attendees,
        )
