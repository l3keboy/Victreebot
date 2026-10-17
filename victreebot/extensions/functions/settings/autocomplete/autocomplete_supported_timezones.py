import lightbulb

from victreebot.contants import MAX_AUTOCOMPLETE_LENGTH

import zoneinfo

from victreebot.core.bot import Bot


# ------------------------------------------------------------------------- #
# AUTOCOMPLETE CALLBACKS #
# ------------------------------------------------------------------------- #
async def autocomplete_supported_timezones(ctx: lightbulb.AutocompleteContext[str], bot: Bot) -> None:
    """Autocomplete callback to return pokemon related to the query."""
    # Validate that the callback is done from a guild
    if ctx.interaction.guild_id is None:
        return

    # Get pokemon list
    supported_timezones = zoneinfo.available_timezones()

    # Build autocomplete options to return
    result_map: dict[str, str] = {}
    for timezone in supported_timezones:
        if len(result_map) == MAX_AUTOCOMPLETE_LENGTH:
            break
        else:
            if timezone.__contains__(str(ctx.focused.value)):
                result_map[f"{timezone}"] = f"{timezone}"

    # Return autocomplete options
    await ctx.respond(result_map)