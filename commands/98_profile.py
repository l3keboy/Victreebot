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
import tanjun
# Functionality
import asyncio
import datetime
# Own Files
from utils import DatabaseHandler, LoggingHandler 
from utils.functions import get_settings, get_profile, validate

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
# PROFILE GROUP COMMAND #
# ------------------------------------------------------------------------- #
profile_group = tanjun.slash_command_group("profile", f"Change details of your profile.")
profile_component = tanjun.Component().add_slash_command(profile_group)


@profile_group.with_command
@tanjun.with_str_slash_option("location_to_add", "The location you want to add.")
@tanjun.as_slash_command("location_add", "Add a location where you are active (for this server ONLY).")
async def command_profile_location_add(ctx: tanjun.abc.Context, location_to_add):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        location = await get_profile.get_location(guild_id=ctx.guild_id, user_id=ctx.member.id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    if location == [] or location is None:
        new_location = location_to_add.capitalize()
    else:
        new_location = location + "," + location_to_add.capitalize()

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            location_to_set = "'" + new_location + "'"
            change_location = f'UPDATE "{ctx.guild_id}" SET location = {location_to_set} WHERE user_id = {ctx.member.id}'
            await conn.fetch(change_location)
    await database.close()

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_profile_location_added.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    response = lang.profile_added_location.format(location=location_to_add.capitalize())
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@profile_group.with_command
@tanjun.with_str_slash_option("location_to_remove", "The location you want to remove.")
@tanjun.as_slash_command("location_remove", "Remove a location from your active locations (for this server ONLY).")
async def command_profle_location_remove(ctx: tanjun.abc.Context, location_to_remove):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        location = await get_profile.get_location(guild_id=ctx.guild_id, user_id=ctx.member.id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    if location == [] or location is None:
        # SEND RESPONSE
        response = lang.profile_no_locations_set
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return
    else:
        location_list = location.split(",")
        if not location_to_remove.capitalize() in location_list:
            response = lang.profile_specified_location_not_found
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
        else:
            location_list.remove(location_to_remove.capitalize())
            if location_list == []:
                new_location = None
            else:
                new_location = location_list

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            if new_location is None:
                change_location = f'UPDATE "{ctx.guild_id}" SET location = NULL WHERE user_id = {ctx.member.id}'
            else:
                location_remove = "'" + ",".join(location for location in new_location) + "'"
                change_location = f'UPDATE "{ctx.guild_id}" SET location = {location_remove} WHERE user_id = {ctx.member.id}'
            await conn.fetch(change_location)
    await database.close()

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_profile_location_removed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    response = lang.profile_removed_location.format(location=location_to_remove.capitalize())
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@profile_group.with_command
@tanjun.with_str_slash_option("friendcode_to_add", "The friend code you want to add. MUST BE IN FORMAT XXXX-XXXX-XXXX!")
@tanjun.as_slash_command("friendcode_add", "Add a friend code to your profile (for this server ONLY).")
async def command_profile_friendcode_add(ctx: tanjun.abc.Context, friendcode_to_add):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        friend_codes = await get_profile.get_friend_codes(guild_id=ctx.guild_id, user_id=ctx.member.id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    success = await validate.__validate_friend_code(friendcode_to_add)
    if not success:
        response = lang.error_friend_code_invalid.format(friend_code=friendcode_to_add)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    if friend_codes == [] or friend_codes is None:
        new_friend_codes = friendcode_to_add
    else:
        new_friend_codes = friend_codes + "," + friendcode_to_add

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            friendcode_to_set = "'" + new_friend_codes + "'"
            change_friend_codes = f'UPDATE "{ctx.guild_id}" SET friend_codes = {friendcode_to_set} WHERE user_id = {ctx.member.id}'
            await conn.fetch(change_friend_codes)
    await database.close()

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_profile_friendcode_added.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    response = lang.profile_added_friend_code.format(friend_code=friendcode_to_add)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@profile_group.with_command
@tanjun.with_str_slash_option("friendcode_to_remove", "The friend code you want to remove. MUST BE IN FORMAT XXXX-XXXX-XXXX!")
@tanjun.as_slash_command("friendcode_remove", "Remove a location from your active locations (for this server ONLY).")
async def command_profle_friendcode_remove(ctx: tanjun.abc.Context, friendcode_to_remove):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        friend_codes = await get_profile.get_friend_codes(guild_id=ctx.guild_id, user_id=ctx.member.id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    success = await validate.__validate_friend_code(friendcode_to_remove)
    if not success:
        response = lang.error_friend_code_invalid.format(friend_code=friendcode_to_remove)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    if friend_codes == [] or friend_codes is None:
        # SEND RESPONSE
        response = lang.profile_no_friend_code_set
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return
    else:
        friendcode_list = friend_codes.split(",")
        if not friendcode_to_remove in friendcode_list:
            response = lang.profile_specified_friend_code_not_found
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
        else:
            friendcode_list.remove(friendcode_to_remove)
            if friendcode_list == []:
                new_friend_codes = None
            else:
                new_friend_codes = friendcode_list

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            if new_friend_codes is None:
                change_friend_codes = f'UPDATE "{ctx.guild_id}" SET friend_codes = NULL WHERE user_id = {ctx.member.id}'
            else:
                friendcode_remove = "'" + ",".join(friend_code for friend_code in new_friend_codes) + "'"
                change_friend_codes = f'UPDATE "{ctx.guild_id}" SET friend_codes = {friendcode_remove} WHERE user_id = {ctx.member.id}'
            await conn.fetch(change_friend_codes)
    await database.close()

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_profile_friendcode_removed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    response = lang.profile_removed_friend_code.format(friend_code=friendcode_to_remove)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()


# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
    client.add_component(profile_component.copy())