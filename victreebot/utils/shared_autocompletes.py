import lightbulb
import pokebase as pb

from victreebot.contants import MAX_AUTOCOMPLETE_LENGTH
from victreebot.core.bot import Bot


# ------------------------------------------------------------------------- #
# AUTOCOMPLETE CALLBACKS #
# ------------------------------------------------------------------------- #
async def autocomplete_pokemon(ctx: lightbulb.AutocompleteContext[str], bot: Bot) -> None:
    """Autocomplete callback to return pokemon related to the query."""
    # Validate that the callback is done from a guild
    if ctx.interaction.guild_id is None:
        return

    # Get pokemon list
    pokemon_list = pb.APIResourceList("pokemon")

    # Build autocomplete options to return
    result_map: dict[str, str] = {}
    for pokemon in pokemon_list:
        if len(result_map) == MAX_AUTOCOMPLETE_LENGTH:
            break
        else:
            if str(ctx.focused.value) in "egg":
                result_map["Egg Normal (Egg1)"] = "egg1"
                result_map["Egg Rare (Egg3)"] = "egg3"
                result_map["Egg Legendary (Egg5)"] = "egg5"
                result_map["Egg Mega (EggMega)"] = "eggmega"
                result_map["Egg Shadow (EggShadow)"] = "eggshadow"
            if pokemon.get("name").__contains__(ctx.focused.value):
                result_map[f"{pokemon.get('name')}"] = f"{pokemon.get('name')}"

    # Return autocomplete options
    await ctx.respond(result_map)


async def autocomplete_locations(ctx: lightbulb.AutocompleteContext[str], bot: Bot) -> None:
    """Autocomplete callback to return pokemon related to the query."""
    # Validate that the callback is done from a guild
    if ctx.interaction.guild_id is None:
        return


    # Get locations
    locations = await bot.database.autocomplete_get_locations_like(ctx.interaction.guild_id, str(ctx.focused.value))

    # Build autocomplete options to return
    result_map: dict[str, str] = {}
    for location in locations:
        if len(result_map) == MAX_AUTOCOMPLETE_LENGTH:
            break
        else:
            result_map[f"{location.type}, {location.name}"] = f"{location.type}, {location.name}"

    # Return autocomplete options
    await ctx.respond(result_map)