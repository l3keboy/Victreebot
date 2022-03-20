# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
# Own Files
from utils.helpers.constants import SUPPORTED_LANGUAGES, SUPPORTED_UNIT_SYSTEMS, SUPPORTED_TIMEZONES
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
# Channel settings #
# ------------------------------------------------------------------------- #
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD, error_message="You need the `Manage Server` permissions to execute this command!")
@tanjun.with_channel_slash_option("channel", f"The new raids channel.")
@tanjun.as_slash_command("raids_channel", f"The channel where {BOT_NAME.capitalize()} sends the raids.")
async def command_settings_update_raids_channel(ctx: tanjun.abc.Context, channel: hikari.InteractionChannel, _db: DatabaseHandler = tanjun.injected(type=DatabaseHandler), _bot: BotUtils = tanjun.injected(type=BotUtils)):
    language, auto_delete, *none = await _db.get_guild_settings(guild=ctx.get_guild(), settings=["language", "auto_delete"])
    log_errors, log_settings_changed, *none = await _db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors", "log_settings_changed"])

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
                await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_raids_channel_failed_not_enough_privileges.format(datetime=await _bot.get_timestamp(), member=ctx.member))
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
                await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_raids_channel_failed_not_a_text_channel.format(datetime=await _bot.get_timestamp(), member=ctx.member))
            return

    if channel is None:
        channel_id = "NULL"
    else:
        channel_id = channel.id
    
    # Change setting
    success = await _db.set_guild_setting(guild=ctx.get_guild(), parameters=[f"raids_channel_id = {channel_id}"])
    if success:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_update_raids_channel_success_changed.format(raids_channel=channel, raids_channel_id=channel_id)
        response_message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(int(auto_delete))
        await response_message.delete()
        if log_settings_changed:
            # Send to log channel
            await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_raids_channel_success_changed.format(datetime=await _bot.get_timestamp(), member=ctx.member, raids_channel=channel, raids_channel_id=channel_id))
    else:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_update_raids_channel_failed_changed.format(raids_channel=channel, raids_channel_id=channel_id)
        response_message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(int(auto_delete))
        await response_message.delete()
        if log_errors:
            # Send to log channel
            await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_update_raids_channel_failed_changed.format(datetime=await _bot.get_timestamp(), member=ctx.member, raids_channel=channel, raids_channel_id=channel_id))


# ------------------------------------------------------------------------- #
# General settings #
# ------------------------------------------------------------------------- #
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD, error_message="You need the `Manage Server` permissions to execute this command!")
@tanjun.with_int_slash_option("auto_delete", f"The time before {BOT_NAME.capitalize()} deletes his responses.", min_value=1, default=None)
@tanjun.with_str_slash_option("unit_system", f"The desired unit system of the server.", choices=[system for system in SUPPORTED_UNIT_SYSTEMS], default=None)
@tanjun.with_str_slash_option("gmt", f"The gmt offset of the server.", choices=[offset for offset in SUPPORTED_TIMEZONES], default=None)
@tanjun.with_str_slash_option("language", f"The language {BOT_NAME.capitalize()} responds in.", choices=[language for language in SUPPORTED_LANGUAGES.keys()], default=None)
@tanjun.as_slash_command("general", f"Update {BOT_NAME.capitalize()}'s general settings.")
async def command_settings_update_general(ctx: tanjun.abc.Context, language: str, gmt: str, unit_system: str, auto_delete: int, _db: DatabaseHandler = tanjun.injected(type=DatabaseHandler), _bot: BotUtils = tanjun.injected(type=BotUtils)):
    language, current_auto_delete, *none = await _db.get_guild_settings(guild=ctx.get_guild(), settings=["language", "auto_delete"])
    log_errors, log_settings_changed, *none = await _db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors", "log_settings_changed"])

    if language is None and gmt is None and unit_system is None and auto_delete is None:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).error_response_settings_update_insert_at_least_1
        response_message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(int(auto_delete))
        await response_message.delete()
        return
    
    parameters=[]
    # Handle new language
    if language is not None:
        language_to_set = "'" + language + "'"
        parameters.append(f'"language" = {language_to_set}')

    # Handle new gmt
    if gmt is not None:
        gmt_to_set = "'" + gmt + "'"
        parameters.append(f'"gmt" = {gmt_to_set}')
    
    # Handle new unit_system
    if unit_system is not None:
        unit_system_to_set = "'" + unit_system + "'"
        parameters.append(f'"unit_system" = {unit_system_to_set}')

    # Handle new auto_delete
    if auto_delete is not None:
        parameters.append(f'"auto_delete" = {auto_delete}')
        current_auto_delete = auto_delete

    success = await _db.set_guild_setting(guild=ctx.get_guild(), parameters=parameters)
    if not success:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_settings_update_general_failed
        response_message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(int(auto_delete))
        await response_message.delete()
        if log_errors:
            # Send to log channel
            await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_general_failed.format(datetime=await _bot.get_timestamp(), member=ctx.member))
        return 

    # Send response
    response = SUPPORTED_LANGUAGES.get(language).response_settings_update_general_success
    response_message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(int(current_auto_delete))
    await response_message.delete()
    if log_settings_changed:
        # Send to log channel
        await _bot.log_from_ctx(ctx, _db, message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_general_success.format(datetime=await _bot.get_timestamp(), member=ctx.member))