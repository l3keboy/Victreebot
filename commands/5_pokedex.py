# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #
# IMPORTS
# Database and .env
import os
from dotenv import load_dotenv
# Hikari
import hikari
import tanjun
# Functionality
import asyncio
import datetime
import aiohttp
import json
import pokebase as pb
# Own Files
from utils import LoggingHandler
from utils.functions import get_settings, pokemon, validate
from utils.config import const

# .ENV AND .ENV VARIABLES
# Load .env
load_dotenv()
# Variables
# Bot Variables
BOT_NAME = os.getenv("BOT_NAME")

component = tanjun.Component()


# ------------------------------------------------------------------------- #
# SLASH COMMANDS #
# ------------------------------------------------------------------------- #
@component.with_slash_command
@tanjun.with_str_slash_option("boss", "The name or ID of the Pokémon to get details off.")
@tanjun.as_slash_command("pokedex", "Search details of a Pokémon.")
async def command_pokedex(ctx: tanjun.abc.Context, boss):
    try:
        lang, gmt, auto_delete_time = await get_settings.get_language_gmt_auto_delete_time_settings(guild_id=ctx.guild_id)
        unit_system = await get_settings.get_unit_system_settings(guild_id=ctx.guild_id)
        raids_channel_id, log_channel_id = await get_settings.get_channels_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    valid_id = await validate.__validate_int(boss)
    if valid_id:
        # VALIDATE POKÉMON
        success, poke_img, pokémon = await pokemon.validate_pokemon_by_id(boss=int(boss))
        if not success:
            response = lang.pokemon_not_found.format(pokemon=boss)
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
    else:
        # VALIDATE POKÉMON
        success, poke_img, pokémon = await pokemon.validate_pokemon_by_name(boss=boss)
        if not success:
            response = lang.pokemon_not_found.format(pokemon=boss.lower())
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return

    # GET POKÉMON DETAILS
    poke_name = pokémon.name
    poke_id = pokémon.id

    poke_height_decimeters = pokémon.height
    poke_weight_hecto_gram = pokémon.weight
    poke_height_meters = poke_height_decimeters / 10
    poke_weight_gram = poke_weight_hecto_gram * 100
    if unit_system == "Metric System":
        heigth_unit = lang.height_metric_system
        weight_unit = lang.weigth_metric_system
        poke_height = round(poke_height_meters, 2)
        poke_weight = round(poke_weight_gram / 1000, 2)
    elif unit_system == "Imperial System":
        heigth_unit = lang.height_imperial_system
        weight_unit = lang.weigth_imperial_system
        poke_height = round(poke_height_meters * 0.3048, 2)
        poke_weight = round(poke_weight_gram * 453.592, 2)
    else:
        heigth_unit = lang.height_united_states_customary_unit_system
        weight_unit = lang.weigth_united_states_customary_unit_system
        poke_height = round(poke_height_meters * 0.0254, 2)
        poke_weight = round(poke_weight_gram * 453.592, 2)

    poke_abilities = []
    poke_all_abilities = pokémon.abilities
    for ability in poke_all_abilities:
        poke_abilities.append(ability.ability)

    # SEND RESPONSE
    if auto_delete_time < 15:
        auto_delete_this_message = 15
    else:
        auto_delete_this_message = auto_delete_time

    embed = (
        hikari.Embed(
            title=lang.pokedex_embed_title.format(pokemon=poke_name.capitalize()),
        )
            .set_footer(
            text=lang.embed_footer.format(member=ctx.member.display_name, auto_delete_time=auto_delete_this_message),
            icon=ctx.member.avatar_url,
        )
            .set_thumbnail(poke_img)
            .add_field(name=lang.pokedex_embed_name_title, value=f"{poke_name.capitalize()}", inline=True)
            .add_field(name=lang.pokedex_embed_id_title, value=f"{poke_id}", inline=True)
            .add_field(name=lang.pokedex_embed_length_weight_title, value=f"{poke_height} {heigth_unit}  |  {poke_weight} {weight_unit}", inline=False)
            .add_field(name=lang.pokedex_embed_abilities_title, value=f"\n".join("- " + str(ability).capitalize() for ability in poke_abilities), inline=True)
            .add_field(name="\n\u200b", value=f"\n\u200b", inline=False)
    )

    try:
        message = await ctx.respond(embed=embed, ensure_result=True)
        await asyncio.sleep(auto_delete_this_message)
        await message.delete()
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send Pokédex response! Got error: {e}")
        # SEND TO LOG CHANNEL
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_pokedex_request_failed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")
        return

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_pokedex_requested.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
