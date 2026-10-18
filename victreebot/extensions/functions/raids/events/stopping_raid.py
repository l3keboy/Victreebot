# Copyright (c) 2022-present l3keboy

import hikari
import lightbulb

from victreebot.core.bot import Bot
from victreebot.models.Raids import RaidsUpdate

loader = lightbulb.Loader()


@loader.listener(hikari.StoppingEvent)
async def stopping_raid(_event: hikari.StoppingEvent, bot: Bot) -> None:
    """Event to offload raids to database from in memory."""
    if len(bot.raids) <= 0:
        return

    for raid in bot.raids:
        raid_class = bot.raids.get(raid)
        if raid_class is None:
            return

        db_raid = await bot.database.get_raid(raid_class.guild_id, raid)
        if db_raid is None:
            return

        instinct_present = None
        if raid_class.instinct_present:
            instinct_present = ",".join(str(instinct) for instinct in raid_class.instinct_present)

        mystic_present = None
        if raid_class.mystic_present:
            mystic_present = ",".join(str(mystic) for mystic in raid_class.mystic_present)

        valor_present = None
        if raid_class.valor_present:
            valor_present = ",".join(str(valor) for valor in raid_class.valor_present)

        remote_present = None
        if raid_class.remote_present:
            remote_present = ",".join(str(remote) for remote in raid_class.remote_present)

        new_raid = RaidsUpdate(
            raid_id=raid_class.raid_id,
            guild_id=raid_class.guild_id,
            instinct_present=instinct_present,
            mystic_present=mystic_present,
            valor_present=valor_present,
            remote_present=remote_present,
            total_attendees=raid_class.total_attendess,
        )

        await bot.database.change_raid(db_raid, new_raid)
