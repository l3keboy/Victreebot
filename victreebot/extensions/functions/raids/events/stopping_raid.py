import hikari
import lightbulb

from victreebot.core.bot import Bot
from victreebot.models.Raids import RaidsUpdate

loader = lightbulb.Loader()


@loader.listener(hikari.StoppingEvent)
async def stopping_raid(event: hikari.StoppingEvent, bot: Bot) -> None:
    """Event to offload raids to database from in memory."""
    if len(bot.raids) <= 0:
        return

    for raid in bot.raids:
        raidClass = bot.raids.get(raid)
        if raidClass is None:
            return

        db_raid = await bot.database.get_raid(raidClass.guild_id, raid)
        if db_raid is None:
            return

        instinct_present = None
        if raidClass.instinct_present:
            instinct_present=",".join(str(instinct) for instinct in raidClass.instinct_present)

        mystic_present = None
        if raidClass.mystic_present:
            mystic_present=",".join(str(mystic) for mystic in raidClass.mystic_present)

        valor_present = None
        if raidClass.valor_present:
            valor_present=",".join(str(valor) for valor in raidClass.valor_present)

        remote_present = None
        if raidClass.remote_present:
            remote_present=",".join(str(remote) for remote in raidClass.remote_present)

        new_raid = RaidsUpdate(
            raid_id=raidClass.raid_id,
            guild_id=raidClass.guild_id,
            instinct_present=instinct_present,
            mystic_present=mystic_present,
            valor_present=valor_present,
            remote_present=remote_present,
            total_attendees=raidClass.total_attendess
        )

        await bot.database.change_raid(db_raid, new_raid)
