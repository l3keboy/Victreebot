# Copyright (c) 2022-present l3keboy

import lightbulb

from victreebot.contants import MAX_AUTOCOMPLETE_LENGTH
from victreebot.core.bot import Bot


# ------------------------------------------------------------------------- #
# AUTOCOMPLETE CALLBACKS #
# ------------------------------------------------------------------------- #
async def autocomplete_raid_id(ctx: lightbulb.AutocompleteContext[str], bot: Bot) -> None:
    """Autocomplete callback to return pokemon related to the query."""
    # Validate that the callback is done from a guild
    if ctx.interaction.guild_id is None:
        return

    # Get raid ids
    raids = await bot.database.autocomplete_get_raid_id_like(ctx.interaction.guild_id, str(ctx.focused.value))

    # Build autocomplete options to return
    result_map: dict[str, str] = {}
    for raid in raids:
        if len(result_map) == MAX_AUTOCOMPLETE_LENGTH:
            break
        result_map[f"{raid.raid_id}"] = f"{raid.raid_id}"

    # Return autocomplete options
    await ctx.respond(result_map)
