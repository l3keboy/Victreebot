# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
# Own Files
from utils.helpers.constants import SUPPORTED_LANGUAGES
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils
# Hikari
import hikari
import tanjun
# Database and .env
import os
from dotenv import load_dotenv
# Functionality
import asyncio


load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")

# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# Log channel setting #
# ------------------------------------------------------------------------- #
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD, error_message="You need the `Manage Server` permissions to execute this command!")
@tanjun.with_channel_slash_option("channel", f"The new logs channel (if no argument is given, the logs channel won't be set).", default=None)
@tanjun.as_slash_command("log_channel", f"Update {BOT_NAME.capitalize()}'s logging channel.")
async def command_log_settings_update_log_channel(ctx: tanjun.abc.Context, channel: hikari.InteractionChannel, _db: DatabaseHandler = tanjun.injected(type=DatabaseHandler), _bot: BotUtils = tanjun.injected(type=BotUtils)):
    language, auto_delete, *none = await _db.get_guild_settings(guild=ctx.get_guild(), settings=["language", "auto_delete"])
    log_errors, log_settings_changed, *none = await _db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors", "log_settings_changed"])

    # Check if guild exists in database
    guild_id, *none = await _db.get_guild_log_settings(ctx.get_guild(), settings=["guild_id"])

    if channel is not None:
        try:
            channel = await ctx.rest.fetch_channel(channel.id)
        except hikari.ForbiddenError:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).error_response_not_enough_permissions_for_channel
            response_message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(int(auto_delete))
            await response_message.delete()
            if log_errors:
                # Send to log channel
                await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_logs_channel_failed_not_enough_privileges.format(datetime=await _bot.get_timestamp(), member=ctx.member))
            return

        desired_type = await _bot.validate_channel_type(channel, hikari.GuildTextChannel)
        if not desired_type:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).error_response_not_a_text_channel
            response_message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(int(auto_delete))
            await response_message.delete()
            if log_errors:
                # Send to log channel
                await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_logs_channel_failed_not_a_text_channel.format(datetime=await _bot.get_timestamp(), member=ctx.member))
            return

    if channel is None:
        channel_id = "NULL"
    else:
        channel_id = channel.id

    # Change setting
    success = await _db.set_guild_log_setting(guild=ctx.get_guild(), parameters=[f"logs_channel_id = {channel_id}"])
    if success:
        if channel is None:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).response_update_logs_channel_success_unset
            response_message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(int(auto_delete))
            await response_message.delete()
            if log_settings_changed:
                # Send to log channel
                await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_logs_channel_success_unset.format(datetime=await _bot.get_timestamp(), member=ctx.member))
        else:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).response_update_logs_channel_success_changed.format(logs_channel=channel, logs_channel_id=channel_id)
            response_message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(int(auto_delete))
            await response_message.delete()
            if log_settings_changed:
                # Send to log channel
                await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_logs_channel_success_changed.format(datetime=await _bot.get_timestamp(), member=ctx.member, logs_channel=channel, logs_channel_id=channel_id))
    else:
        if channel is None:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).response_update_logs_channel_failed_unset
            response_message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(int(auto_delete))
            await response_message.delete()
            if log_errors:
                # Send to log channel
                await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_logs_channel_failed_unset.format(datetime=await _bot.get_timestamp(), member=ctx.member))
        else:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).response_update_logs_channel_failed_changed.format(logs_channel=channel, logs_channel_id=channel_id)
            response_message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(int(auto_delete))
            await response_message.delete()
            if log_errors:
                # Send to log channel
                await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_logs_channel_failed_changed.format(datetime=await _bot.get_timestamp(), member=ctx.member, logs_channel=channel, logs_channel_id=channel_id))

# ------------------------------------------------------------------------- #
# General events log_settings #
# ------------------------------------------------------------------------- #
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD, error_message="You need the `Manage Server` permissions to execute this command!")
@tanjun.with_bool_slash_option("log_settings_changed", "If settings changes should be logged.", default=None)
@tanjun.with_bool_slash_option("log_info", "If info requests should be logged (Note! This is for all info commands AND ping!).", default=None)
@tanjun.with_bool_slash_option("log_errors", "If errors should be logged (e.g. a change or command failed).", default=None)
@tanjun.as_slash_command("general_events", f"Update {BOT_NAME.capitalize()}'s general events settings.")
async def command_log_settings_update_general_events(ctx: tanjun.abc.Context, log_errors: bool, log_info: bool, log_settings_changed: bool, _db: DatabaseHandler = tanjun.injected(type=DatabaseHandler), _bot: BotUtils = tanjun.injected(type=BotUtils)):
    language, auto_delete, *none = await _db.get_guild_settings(guild=ctx.get_guild(), settings=["language", "auto_delete"])
    
    # Check if guild exists in database
    guild_id, *none = await _db.get_guild_log_settings(ctx.get_guild(), settings=["guild_id"])

    if log_errors is None and log_info is None and log_settings_changed is None and log_support is None:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).error_response_settings_update_insert_at_least_1
        response_message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(int(auto_delete))
        await response_message.delete()
        return

    parameters=[]
    # Handle new log_errors
    if log_errors is not None:
        parameters.append(f'"log_errors" = {log_errors}')

    # Handle new log_info
    if log_info is not None:
        parameters.append(f'"log_info" = {log_info}')
    
    # Handle new log_settings_changed
    if log_settings_changed is not None:
        parameters.append(f'"log_settings_changed" = {log_settings_changed}')

    success = await _db.set_guild_log_setting(guild=ctx.get_guild(), parameters=parameters)
    if not success:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_log_settings_update_general_events_failed
        response_message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(int(auto_delete))
        await response_message.delete()
        if log_errors:
            # Send to log channel
            await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_log_settings_update_general_events_failed.format(datetime=await _bot.get_timestamp(), member=ctx.member))
        return 

    # Send response
    response = SUPPORTED_LANGUAGES.get(language).response_log_settings_update_general_events_success
    response_message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(int(auto_delete))
    await response_message.delete()
    if log_settings_changed:
        # Send to log channel
        await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_log_settings_update_general_events_success.format(datetime=await _bot.get_timestamp(), member=ctx.member))