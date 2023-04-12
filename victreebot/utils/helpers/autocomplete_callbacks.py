# IMPORTS
import pokebase as pb
import hikari
import tanjun
from core.bot import Bot
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils


# ------------------------------------------------------------------------- #
# AUTOCOMPLETE CALLBACKS #
# ------------------------------------------------------------------------- #
async def autocomplete_location(
    ctx: tanjun.abc.AutocompleteContext,
    query: str,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
) -> None:
    if ctx.guild_id is None:
        return

    locations_like = await db.get_locations_like(guild=ctx.get_guild(), query=query)

    if locations_like == [] or locations_like is None:
        return None

    result_map: dict[str, str] = {}
    for location in locations_like:
        if len(result_map) == 25:
            break
        else:
            result_map[
                f"{location.get('type')}, {location.get('name')}"
            ] = f"{location.get('type')}, {location.get('name')}"

    await ctx.set_choices(result_map)


async def autocomplete_raid_id(
    ctx: tanjun.abc.AutocompleteContext,
    query: str,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
) -> None:
    if ctx.guild_id is None:
        return

    raid_ids_like = await db.get_raid_id_like(guild=ctx.get_guild(), query=query)

    if raid_ids_like == [] or raid_ids_like is None:
        return None

    result_map: dict[str, str] = {}
    for raid_id in raid_ids_like:
        if len(result_map) == 25:
            break
        else:
            result_map[f"{raid_id.get('raid_id')}"] = f"{raid_id.get('raid_id')}"

    await ctx.set_choices(result_map)


async def autocomplete_pokemon(
    ctx: tanjun.abc.AutocompleteContext,
    query: str,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
) -> None:
    if ctx.guild_id is None:
        return

    pokemon_list = pb.APIResourceList("pokemon")

    result_map: dict[str, str] = {}
    for pokemon in pokemon_list:
        if len(result_map) == 25:
            break
        else:
            if query in "egg":
                result_map["Egg Normal (Egg1)"] = "egg1"
                result_map["Egg Rare (Egg3)"] = "egg3"
                result_map["Egg Legendary (Egg5)"] = "egg5"
                result_map["Egg Mega (EggMega)"] = "eggmega"
            if pokemon.get("name").__contains__(query):
                result_map[f"{pokemon.get('name')}"] = f"{pokemon.get('name')}"

    await ctx.set_choices(result_map)
