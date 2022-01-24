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
from PIL import Image
import aiohttp
from io import BytesIO
# Own Files
from utils import LoggingHandler
from utils.functions import get_settings, pokemon, validate

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
# ------------------------------------------------------------------------- #
# TRADE GROUP COMMAND #
# ------------------------------------------------------------------------- #
trade_group = tanjun.slash_command_group("trade", f"Ask other users for a trade.")
trade_component = tanjun.Component().add_slash_command(trade_group)


@trade_group.with_command
@tanjun.with_str_slash_option("pokémon_want", "The name or ID of the Pokémon you want to have.")
@tanjun.with_str_slash_option("pokémon_have", "The name or ID of the Pokémon you have to offer.")
@tanjun.as_slash_command("proposal", "Propose a trade to other server users.")
async def command_trade_proposal(ctx: tanjun.abc.Context, pokémon_have, pokémon_want):
    try:
        lang, gmt, auto_delete_time = await get_settings.get_language_gmt_auto_delete_time_settings(guild_id=ctx.guild_id)
        raids_channel_id, log_channel_id = await get_settings.get_channels_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    valid_id = await validate.__validate_int(pokémon_have)
    if valid_id:
        # VALIDATE POKÉMON
        success, poke_img_have, pokémon_have = await pokemon.validate_pokemon_by_id(boss=int(pokémon_have))
        if not success:
            response = lang.pokemon_not_found.format(pokemon=pokémon_have)
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
    else:
        # VALIDATE POKÉMON
        success, poke_img_have, pokémon_have = await pokemon.validate_pokemon_by_name(boss=pokémon_have)
        if not success:
            response = lang.pokemon_not_found.format(pokemon=pokémon_have.lower())
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return

    valid_id = await validate.__validate_int(pokémon_want)
    if valid_id:
        # VALIDATE POKÉMON
        success, poke_img_want, pokémon_want = await pokemon.validate_pokemon_by_id(boss=int(pokémon_want))
        if not success:
            response = lang.pokemon_not_found.format(pokemon=pokémon_want)
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
    else:
        # VALIDATE POKÉMON
        success, poke_img_want, pokémon_want = await pokemon.validate_pokemon_by_name(boss=pokémon_want)
        if not success:
            response = lang.pokemon_not_found.format(pokemon=pokémon_want.lower())
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return

    async with aiohttp.ClientSession() as session:
        async with session.get(poke_img_have) as response:
            poke_img_have_request = await response.read()
    async with aiohttp.ClientSession() as session:
        async with session.get(poke_img_want) as response:
            poke_img_want_request = await response.read()

    poke_img_have_image = Image.open(BytesIO(poke_img_have_request))
    poke_img_want_image = Image.open(BytesIO(poke_img_want_request))
    combined_image = Image.new('RGBA', (5*poke_img_have_image.size[0], poke_img_have_image.size[1]), (0,0,0,0))
    combined_image.paste(poke_img_have_image, (0,0))
    combined_image.paste(poke_img_want_image, (poke_img_have_image.size[0]+200, 0))

    combined_image_bytes = BytesIO()
    combined_image.save(combined_image_bytes, "PNG")
    combined_image_bytes = combined_image_bytes.getvalue()

    embed = (
        hikari.Embed(
            title=lang.trade_proposal_embed_title,
            description=lang.trade_proposal_embed_description.format(pokémon_have=pokémon_have.name, pokémon_want=pokémon_want.name)
        )
            .set_footer(
            text=lang.trade_proposal_embed_footer.format(member=ctx.member.display_name),
        )
            .set_thumbnail()
            .add_field(name=lang.trade_proposal_embed_offering, value=f"{pokémon_have.name}", inline=True)
            .add_field(name="<->", value="\u200b", inline=True)
            .add_field(name=lang.trade_proposal_embed_looking_for, value=f"{pokémon_want.name}", inline=True)
            .set_image(combined_image_bytes)
        )

    message1 = await ctx.respond(ctx.member.mention + lang.trade_proposal_created, ensure_result=True)
    message2 = await ctx.get_channel().send(embed=embed)

    # SEND MESSAGE TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_trade_proposal_created.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

@trade_group.with_command
@tanjun.with_str_slash_option("pokémon_have", "The name or ID of the Pokémon you have to offer.")
@tanjun.as_slash_command("offer", "Offer a Pokémon to trade.")
async def command_trade_offer(ctx: tanjun.abc.Context, pokémon_have):
    try:
        lang, gmt, auto_delete_time = await get_settings.get_language_gmt_auto_delete_time_settings(guild_id=ctx.guild_id)
        raids_channel_id, log_channel_id = await get_settings.get_channels_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    valid_id = await validate.__validate_int(pokémon_have)
    if valid_id:
        # VALIDATE POKÉMON
        success, poke_img_have, pokémon_have = await pokemon.validate_pokemon_by_id(boss=int(pokémon_have))
        if not success:
            response = lang.pokemon_not_found.format(pokemon=pokémon_have)
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
    else:
        # VALIDATE POKÉMON
        success, poke_img_have, pokémon_have = await pokemon.validate_pokemon_by_name(boss=pokémon_have)
        if not success:
            response = lang.pokemon_not_found.format(pokemon=pokémon_have.lower())
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return

    embed = (
        hikari.Embed(
            title=lang.trade_offer_embed_title,
            description=lang.trade_offer_embed_description.format(pokémon_have=pokémon_have.name)
        )
            .set_footer(
            text=lang.trade_offer_embed_footer.format(member=ctx.member.display_name),
        )
            .set_thumbnail()
            .add_field(name=lang.trade_offer_embed_offering, value=f"{pokémon_have.name}", inline=True)
            .set_image(poke_img_have)
        )

    message1 = await ctx.respond(ctx.member.mention + lang.trade_offer_created, ensure_result=True)
    await message1.delete()
    message2 = await ctx.get_channel().send(embed=embed)

    # SEND MESSAGE TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_trade_offer_created.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

@trade_group.with_command
@tanjun.with_str_slash_option("pokémon_want", "The name or ID of the Pokémon you want to have.")
@tanjun.as_slash_command("search", "Search for a Pokémon to trade.")
async def command_trade_offer(ctx: tanjun.abc.Context, pokémon_want):
    try:
        lang, gmt, auto_delete_time = await get_settings.get_language_gmt_auto_delete_time_settings(guild_id=ctx.guild_id)
        raids_channel_id, log_channel_id = await get_settings.get_channels_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    valid_id = await validate.__validate_int(pokémon_want)
    if valid_id:
        # VALIDATE POKÉMON
        success, poke_img_want, pokémon_want = await pokemon.validate_pokemon_by_id(boss=int(pokémon_want))
        if not success:
            response = lang.pokemon_not_found.format(pokemon=pokémon_want)
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
    else:
        # VALIDATE POKÉMON
        success, poke_img_want, pokémon_want = await pokemon.validate_pokemon_by_name(boss=pokémon_want)
        if not success:
            response = lang.pokemon_not_found.format(pokemon=pokémon_want.lower())
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return

    embed = (
        hikari.Embed(
            title=lang.trade_search_embed_title,
            description=lang.trade_search_embed_description.format(pokémon_want=pokémon_want.name)
        )
            .set_footer(
            text=lang.trade_search_embed_footer.format(member=ctx.member.display_name),
        )
            .set_thumbnail()
            .add_field(name=lang.trade_search_embed_looking_for, value=f"{pokémon_want.name}", inline=True)
            .set_image(poke_img_want)
        )

    message1 = await ctx.respond(ctx.member.mention + lang.trade_search_created, ensure_result=True)
    message2 = await ctx.get_channel().send(embed=embed)

    # SEND MESSAGE TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_trade_search_created.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")


# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
    client.add_component(trade_component.copy())