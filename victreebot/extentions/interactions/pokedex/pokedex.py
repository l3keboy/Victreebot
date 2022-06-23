# IMPORTS
import os

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.with_str_slash_option("boss", "The name or ID of the Pokémon to get details off.")
@tanjun.as_slash_command("pokedex", "Search details of a pokémon")
async def command_pokedex(
    ctx: tanjun.abc.SlashContext,
    boss: str,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, unit_system, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "unit_system", "is_setup"]
    )
    log_errors, log_info, *none = await db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors", "log_info"])

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    try:
        int(boss)
        boss = int(boss)
    except Exception:
        boss = boss.replace(" ", "-")
        boss = boss.lower()

    success, pokemon, pokemon_image = await bot.validate_pokemon(boss)
    if not success:
        response = SUPPORTED_LANGUAGES.get(language).response_pokedex_unknown_pokemon.format(boss_name=boss)
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_pokedex_unknown_pokemon.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return

    pokemon_name = pokemon.name
    pokemon_id = pokemon.id

    pokemon_height_decimeters = pokemon.height
    pokemon_weight_hecto_gram = pokemon.weight
    pokemon_height_meters = pokemon_height_decimeters / 10
    pokemon_weight_gram = pokemon_weight_hecto_gram * 100
    if unit_system == "Metric System":
        height_unit = SUPPORTED_LANGUAGES.get(language).height_metric_system
        weight_unit = SUPPORTED_LANGUAGES.get(language).weight_metric_system
        pokemon_height = round(pokemon_height_meters, 2)
        pokemon_weight = round(pokemon_weight_gram / 1000, 2)
    elif unit_system == "Imperial System":
        height_unit = SUPPORTED_LANGUAGES.get(language).height_imperial_system
        weight_unit = SUPPORTED_LANGUAGES.get(language).weight_imperial_system
        pokemon_height = round(pokemon_height_meters, *0.3048, 3)
        pokemon_weight = round(pokemon_weight_gram * 453.592, 2)
    else:
        height_unit = SUPPORTED_LANGUAGES.get(language).height_usc_system
        weight_unit = SUPPORTED_LANGUAGES.get(language).weight_usc_system
        pokemon_height = round(pokemon_height_meters * 0.0254, 2)
        pokemon_weight = round(pokemon_weight_gram * 453.592, 2)

    pokemon_abilities = []
    pokemon_all_abilities = pokemon.abilities
    for ability in pokemon_all_abilities:
        pokemon_abilities.append(ability.ability)

    auto_delete = 20 if auto_delete < 20 else auto_delete

    embed = (
        hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).pokedex_embed_title.format(pokemon=pokemon_name.capitalize()),
            colour=hikari.Colour(0x8BC683),
        )
        .set_thumbnail(pokemon_image)
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).pokedex_embed_name_title,
            value=f"{pokemon_name.capitalize()}",
            inline=True,
        )
        .add_field(name=SUPPORTED_LANGUAGES.get(language).pokedex_embed_id_title, value=f"{pokemon_id}", inline=True)
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).pokedex_embed_length_weight_title,
            value=f"{pokemon_height} {height_unit}  |  {pokemon_weight} {weight_unit}",
            inline=False,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).pokedex_embed_abilities_title,
            value="\n".join("- " + str(ability).capitalize() for ability in pokemon_abilities),
            inline=True,
        )
    )

    await ctx.respond(embed=embed, delete_after=int(auto_delete))
    if log_info:
        # Send to log channel
        await bot.log_from_ctx(
            ctx,
            db,
            message=SUPPORTED_LANGUAGES.get(language).log_response_pokedex_requested.format(
                datetime=await bot.get_timestamp(), member=ctx.member
            ),
        )
