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
import asyncpg
from dotenv import load_dotenv
# Hikari
import hikari
import tanjun
# Functionality
import asyncio
import math
import datetime
# Own Files
from utils import DatabaseHandler, LoggingHandler 
from utils.functions import get_settings, validate
from utils.config import const

# .ENV AND .ENV VARIABLES
# Load .env
load_dotenv()
# Variables
# Bot Variables
BOT_NAME = os.getenv("BOT_NAME")

component = tanjun.Component()

# ------------------------------------------------------------------------- #
# FUNCTIONS COMMANDS #
# ------------------------------------------------------------------------- #
async def __create(location_type, guild_id, name, latitude, longitude):
    success = False
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                name_to_set = "'" + name.replace("'", "''") + "'"
                create_query = f'INSERT INTO "{location_type}" (guild_id, name, latitude, longitude) VALUES ({guild_id}, {name_to_set}, {latitude}, {longitude})'
                await conn.fetch(create_query)
                success = True
            except Exception as e:
                success = False
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while creating a {location_type} for guild_id: {guild_id}! Error: {e} -- Query: {create_query}")
    await database.close()
    return success


async def __delete(location_type, guild_id, name):
    success = False
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                name_to_delete = "'" + name + "'"
                delete_query = f'DELETE FROM "{location_type}" WHERE guild_id = {guild_id} AND name = {name_to_delete}'
                await conn.fetch(delete_query)
                success = True
            except Exception as e:
                success = False
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while deleting a {location_type} for guild_id: {guild_id}! Error: {e}")
    await database.close()
    return success


# ------------------------------------------------------------------------- #
# SLASH COMMANDS #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# LOCATION GROUP COMMAND #
# ------------------------------------------------------------------------- #
location_group = tanjun.slash_command_group("location", f"Create/Delete/Get info about a location.")
location_component = tanjun.Component().add_slash_command(location_group)


@location_group.with_command
@tanjun.with_str_slash_option("longitude", "The longitude of the location.")
@tanjun.with_str_slash_option("latitude", "The latitude of the location.")
@tanjun.with_str_slash_option("name", "The name of the location.")
@tanjun.with_str_slash_option("location_type", "The type of the location.", choices=[loc_type for loc_type in const.LOCATION_TYPES])
@tanjun.as_slash_command("create", "Create a location.")
async def command_location_create(ctx: tanjun.abc.Context, location_type, name, latitude, longitude):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    
    # VALIDATE FLOAT OF LATITUDE LONGITUDE
    valid_float_latitude, valid_float_longitude = await validate.__float_latitude_longitude_check(latitude=latitude, longitude=longitude)
    if not valid_float_latitude:
        response = lang.error_float_latitude_invalid.format(latitude=latitude)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return
    if not valid_float_longitude:
        response = lang.error_float_longitude_invalid.format(latitude=latitude)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    # VALIDATE LATITUDE LONGITUDE
    valid_latitude, valid_longitude = await validate.__latitude_longitude_check(latitude=float(latitude), longitude=float(longitude))
    if not valid_latitude:
        response = lang.error_latitude_invalid.format(latitude=latitude)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return
    if not valid_longitude:
        response = lang.error_longitude_invalid.format(longitude=longitude)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    # NAME HANDLER
    name_to_set = name.lower()

    # CREATE LOCATION
    status = await __create(location_type=location_type, guild_id=ctx.guild_id, name=name_to_set, latitude=latitude, longitude=longitude)
    if status:
        response = lang.create_success.format(location_type=location_type)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()

        # SEND TO LOG CHANNEL
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_location_successfully_created.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, location_type=location_type, name=name_to_set))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")
    else:
        response = lang.create_failed.format(location_type=location_type)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()

        # SEND TO LOG CHANNEL
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_location_creation_failed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, location_type=location_type, name=name_to_set))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

@location_group.with_command
@tanjun.with_str_slash_option("name", "The name of the location.")
@tanjun.with_str_slash_option("location_type", "The type of the location.", choices=[loc_type for loc_type in const.LOCATION_TYPES])
@tanjun.as_slash_command("delete", "Delete a location.")
async def command_location_delete(ctx: tanjun.abc.Context, location_type, name):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    # NAME HANDLER
    name_to_delete = name.lower()

    # CREATE LOCATION
    status = await __delete(location_type=location_type, guild_id=ctx.guild_id, name=name_to_delete)
    if status:
        response = lang.delete_success.format(location_type=location_type)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()

        # SEND TO LOG CHANNEL
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_location_successfully_deleted.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, location_type=location_type, name=name_to_delete))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")
    else:
        response = lang.delete_failed.format(location_type=location_type)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()

        # SEND TO LOG CHANNEL
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_location_deletion_failed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, location_type=location_type, name=name_to_delete))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

@location_group.with_command
@tanjun.with_str_slash_option("name", "The name of the location. No arguments will show a list of all location types.", default=None)
@tanjun.with_str_slash_option("location_type", "The type of the location.", choices=[loc_type for loc_type in const.LOCATION_TYPES])
@tanjun.as_slash_command("info", "Get info about location.")
async def command_location_info(ctx: tanjun.abc.Context, location_type, name):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_location_info_request.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, location_type=location_type))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # INFO HANDLER
    if name is not None:
        if auto_delete_time < 15:
            auto_delete_this_message = 15
        else:
            auto_delete_this_message = auto_delete_time
        database = await DatabaseHandler.acquire_database()
        async with database.acquire() as conn:
            async with conn.transaction():
                try:
                    name_to_find = "'"+ name.lower() +"'"
                    select_location_type_info = f'SELECT latitude, longitude FROM "{location_type}" WHERE guild_id = {ctx.guild_id} and name = {name_to_find}'
                    fetched_info = await conn.fetch(select_location_type_info)

                    if fetched_info == []:
                        raise asyncpg.exceptions.UndefinedColumnError
                    else:   
                        latitude = fetched_info[0].get("latitude")
                        longitude = fetched_info[0].get("longitude")
                        exists = True
                except asyncpg.exceptions.UndefinedColumnError:
                    LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Guild_id {ctx.guild_id} asked location information about a non existing location!")
                    exists = False
        await database.close()
        
        if not exists:
            response = lang.info_embed_location_does_not_exists.format(location=name.lower(), location_type=location_type)
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
        else:
            embed = (
                hikari.Embed(
                    title=lang.location_info_embed_title,
                    description=lang.location_info_embed_discription.format(location=name.lower(), location_type=location_type)
                )
                    .set_footer(
                    text=lang.embed_footer.format(member=ctx.member.display_name, auto_delete_time=auto_delete_this_message),
                )
                    .set_thumbnail()
                    .add_field(name=lang.location_info_embed_location_info_field_title, value=lang.location_info_embed_location_info_field_value.format(latitude=latitude, longitude=longitude), inline=False)
                    .add_field(name=lang.location_info_embed_location_google_maps_field_title, value=f"[{lang.location_info_google_maps}](https://www.google.com/maps/place/@{latitude},{longitude})", inline=False)
            )
            message = await ctx.respond(embed=embed, ensure_result=True)
            await asyncio.sleep(auto_delete_this_message)
            await message.delete()
    else:
        database = await DatabaseHandler.acquire_database()
        async with database.acquire() as conn:
            async with conn.transaction():
                select_location_type_info = f'SELECT name, latitude, longitude FROM "{location_type}" WHERE guild_id = {ctx.guild_id} ORDER BY name ASC '
                fetched_info = await conn.fetch(select_location_type_info)
        await database.close()

        if fetched_info == []:
            response = lang.location_info_paginate_embed_no_results.format(location_type=location_type)
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
        elif len(fetched_info) < 11:
            if auto_delete_time < 15:
                auto_delete_this_message = 15
            else:
                auto_delete_this_message = auto_delete_time
            embed = (
                hikari.Embed(
                    title=lang.location_info_paginate_embed_title,
                    description=lang.location_info_paginate_embed_description
                )
                    .set_footer(
                    text=lang.embed_footer.format(member=ctx.member.display_name, auto_delete_time=auto_delete_this_message)
                )
                    .set_thumbnail()
                    .add_field(name=lang.location_info_paginate_embed_locations_title, value=f"\n".join(f"***{location.get('name')}***" + " \n" + f"[{lang.location_info_google_maps}](https://www.google.com/maps/place/{location.get('latitude')},{location.get('longitude')})" + "\n" for location in fetched_info), inline=False)
            )
            message = await ctx.respond(embed=embed, ensure_result=True)
            await asyncio.sleep(auto_delete_this_message)
            await message.delete()
        else:
            if auto_delete_time < 45:
                auto_delete_this_message = 45
            else:
                auto_delete_this_message = auto_delete_time

            i, start, end, max_length = 1, 0, 10, 10
            values = []
            pages = math.ceil(len(fetched_info)/max_length)
            
            while i <= pages:
                embed = (
                    hikari.Embed(
                        title=lang.location_info_paginate_embed_title,
                        description=lang.location_info_paginate_embed_description
                    )
                        .set_footer(
                        text=lang.embed_footer.format(member=ctx.member.display_name, auto_delete_time=auto_delete_this_message)
                    )
                        .set_thumbnail()
                        .add_field(name=lang.location_info_paginate_embed_locations_title, value=f"\n".join(f"***{location.get('name')}***" + " \n" + f"[{lang.location_info_google_maps}](https://www.google.com/maps/place/{location.get('latitude')},{location.get('longitude')})" + "\n" for location in fetched_info[start:end]), inline=False)
                )
                start += 10
                end += 10
                i += 1
                values.append(embed)

            index = 0
            button_menu = (
                ctx.rest.build_action_row()
                .add_button(hikari.messages.ButtonStyle.SECONDARY, "<<")
                .set_label("<<")
                .add_to_container()
                .add_button(hikari.messages.ButtonStyle.PRIMARY, "<")
                .set_label("<")
                .add_to_container()
                .add_button(hikari.messages.ButtonStyle.PRIMARY, ">")
                .set_label(">")
                .add_to_container()
                .add_button(hikari.messages.ButtonStyle.SECONDARY, ">>")
                .set_label(">>")
                .add_to_container()
            )

            await ctx.respond(values[0], component=button_menu)

            while True:
                try:
                    event = await ctx.client.events.wait_for(hikari.InteractionCreateEvent, timeout=auto_delete_this_message)
                except asyncio.TimeoutError:
                    await ctx.delete_initial_response()
                    return
                else:
                    if isinstance(event.interaction, hikari.CommandInteraction):
                        await ctx.delete_initial_response()
                        return
                    elif event.interaction.custom_id == "<<":
                        index = 0
                    elif event.interaction.custom_id == "<":
                        index = (index - 1) % len(values)
                    elif event.interaction.custom_id == ">":
                        index = (index + 1) % len(values)
                    elif event.interaction.custom_id == ">>":
                        index = len(values) - 1

                    await ctx.edit_initial_response(values[index])
                    await event.interaction.create_initial_response(
                        hikari.interactions.base_interactions.ResponseType.DEFERRED_MESSAGE_UPDATE,
                        values[index]
                    )


# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
    client.add_component(location_component.copy())