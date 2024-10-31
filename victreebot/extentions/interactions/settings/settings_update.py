# IMPORTS
import os

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES
from utils.helpers.contants import SUPPORTED_TIMEZONES
from utils.helpers.contants import SUPPORTED_UNIT_SYSTEMS

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# General settings #
# ------------------------------------------------------------------------- #
@tanjun.with_author_permission_check(
    hikari.Permissions.MANAGE_GUILD, error_message="You need the `Manage Server` permissions to execute this command!"
)
@tanjun.with_role_slash_option("moderator_role", f"The {BOT_NAME.capitalize()} moderator role.", default=None)
@tanjun.with_int_slash_option(
    "auto_delete", f"The time before {BOT_NAME.capitalize()} deletes his responses.", min_value=1, default=None
)
@tanjun.with_str_slash_option(
    "unit_system",
    "The desired unit system of the server.",
    choices=[system for system in SUPPORTED_UNIT_SYSTEMS],
    default=None,
)
@tanjun.with_str_slash_option(
    "gmt", "The gmt offset of the server.", choices=[offset for offset in SUPPORTED_TIMEZONES], default=None
)
@tanjun.with_str_slash_option(
    "language",
    f"The language {BOT_NAME.capitalize()} responds in.",
    choices=[language for language in SUPPORTED_LANGUAGES.keys()],
    default=None,
)
@tanjun.as_slash_command("general", f"Update {BOT_NAME.capitalize()}'s general settings.")
async def command_settings_update_general(
    ctx: tanjun.abc.SlashContext,
    language: str,
    gmt: str,
    unit_system: str,
    auto_delete: int,
    moderator_role: hikari.Role,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
):
    language, current_auto_delete, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "is_setup"]
    )
    log_errors, log_settings_changed, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_settings_changed"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    if language is None and gmt is None and unit_system is None and auto_delete is None and moderator_role is None:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).error_response_settings_update_insert_at_least_1
        await ctx.respond(response, ensure_result=True, delete_after=int(auto_delete))
        if log_errors:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_general_failed.format(
                    datetime=await bot.get_timestamp(), member=ctx.member
                ),
            )
        return

    parameters = []
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

    # Handle new moderator_role
    if moderator_role is not None:
        parameters.append(f'"moderator_role_id" = {moderator_role.id}')

    success = await db.set_guild_setting(guild=ctx.get_guild(), parameters=parameters)
    if not success:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_settings_update_general_failed
        await ctx.respond(response, ensure_result=True, delete_after=int(auto_delete))
        if log_errors:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_general_failed.format(
                    datetime=await bot.get_timestamp(), member=ctx.member
                ),
            )
        return

    # Send response
    response = SUPPORTED_LANGUAGES.get(language).response_settings_update_general_success
    await ctx.respond(response, ensure_result=True, delete_after=int(current_auto_delete))
    if log_settings_changed:
        # Send to log channel
        await bot.log_from_ctx(
            ctx,
            db,
            message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_general_success.format(
                datetime=await bot.get_timestamp(), member=ctx.member
            ),
        )


# ------------------------------------------------------------------------- #
# Raids settings #
# ------------------------------------------------------------------------- #
@tanjun.with_author_permission_check(
    hikari.Permissions.MANAGE_GUILD, error_message="You need the `Manage Server` permissions to execute this command!"
)
@tanjun.with_bool_slash_option(
    "extended_time_format", f"Do you want to use simple or extended time format?", default=None
)
@tanjun.with_int_slash_option(
    "raid_timeout",
    f"The time {BOT_NAME.capitalize()} waits before deleting a raid after it ended (in seconds!).",
    min_value=0,
    default=None,
)
@tanjun.with_str_slash_option("valor_emoji", f"The {BOT_NAME.capitalize()} valor emoji.", default=None)
@tanjun.with_str_slash_option("mystic_emoji", f"The {BOT_NAME.capitalize()} mystic emoji.", default=None)
@tanjun.with_str_slash_option("instinct_emoji", f"The {BOT_NAME.capitalize()} instinct emoji.", default=None)
@tanjun.with_role_slash_option("valor_role", f"The {BOT_NAME.capitalize()} valor role.", default=None)
@tanjun.with_role_slash_option("mystic_role", f"The {BOT_NAME.capitalize()} mystic role.", default=None)
@tanjun.with_role_slash_option("instinct_role", f"The {BOT_NAME.capitalize()} instinct role.", default=None)
@tanjun.as_slash_command("raid", f"Update {BOT_NAME.capitalize()}'s raid settings.")
async def command_settings_update_raid(
    ctx: tanjun.abc.SlashContext,
    instinct_role: hikari.Role,
    mystic_role: hikari.Role,
    valor_role: hikari.Role,
    instinct_emoji: str,
    mystic_emoji: str,
    valor_emoji: str,
    raid_timeout: int,
    extended_time_format: bool,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete"]
    )
    log_errors, log_settings_changed, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_settings_changed"]
    )

    if (
        instinct_role is None
        and mystic_role is None
        and valor_role is None
        and instinct_emoji is None
        and mystic_emoji is None
        and valor_emoji is None
        and raid_timeout is None
        and extended_time_format is None
    ):
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).error_response_settings_update_insert_at_least_1
        await ctx.respond(response, ensure_result=True, delete_after=int(auto_delete))
        if log_errors:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_general_failed.format(
                    datetime=await bot.get_timestamp(), member=ctx.member
                ),
            )
        return

    filtered_raids = [raid for raid in bot_aware.raids.values() if raid is not None and raid.guild == ctx.get_guild()]

    if filtered_raids != []:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_settings_update_raid_failed_raids_active
        await ctx.respond(response, ensure_result=True, delete_after=int(auto_delete))
        if log_errors:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_raid_failed_raids_active.format(
                    datetime=await bot.get_timestamp(), member=ctx.member
                ),
            )
        return

    parameters = []
    # Handle new instinct_role
    if instinct_role is not None:
        parameters.append(f'"instinct_role_id" = {instinct_role.id}')

    # Handle new mystic_role
    if mystic_role is not None:
        parameters.append(f'"mystic_role_id" = {mystic_role.id}')

    # Handle new valor_role
    if valor_role is not None:
        parameters.append(f'"valor_role_id" = {valor_role.id}')

    # Handle new instinct_emoji
    if instinct_emoji is not None:
        instinct_emoji_id = filter(str.isdigit, instinct_emoji)
        instinct_emoji_id = "".join(instinct_emoji_id)
        emoji = ctx.cache.get_emoji(instinct_emoji_id) or await ctx.rest.fetch_emoji(ctx.get_guild(), instinct_emoji_id)
        parameters.append(f'"instinct_emoji_id" = {emoji.id}')

    # Handle new mystic_emoji
    if mystic_emoji is not None:
        mystic_emoji_id = filter(str.isdigit, mystic_emoji)
        mystic_emoji_id = "".join(mystic_emoji_id)
        emoji = ctx.cache.get_emoji(mystic_emoji_id) or await ctx.rest.fetch_emoji(ctx.get_guild(), mystic_emoji_id)
        parameters.append(f'"mystic_emoji_id" = {emoji.id}')

    # Handle new valor_emoji
    if valor_emoji is not None:
        valor_emoji_id = filter(str.isdigit, valor_emoji)
        valor_emoji_id = "".join(valor_emoji_id)
        emoji = ctx.cache.get_emoji(valor_emoji_id) or await ctx.rest.fetch_emoji(ctx.get_guild(), valor_emoji_id)
        parameters.append(f'"valor_emoji_id" = {emoji.id}')

    # Handle new raid_timeout
    if raid_timeout is not None:
        parameters.append(f'"raid_timeout" = {raid_timeout}')

    # Handle new extended_time_format
    if extended_time_format is not None:
        parameters.append(f'"extended_time_format" = {extended_time_format}')

    success = await db.set_guild_setting(guild=ctx.get_guild(), parameters=parameters)
    if not success:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_settings_update_raid_failed
        await ctx.respond(response, ensure_result=True, delete_after=int(auto_delete))
        if log_errors:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_raid_failed.format(
                    datetime=await bot.get_timestamp(), member=ctx.member
                ),
            )
        return

    # Send response
    response = SUPPORTED_LANGUAGES.get(language).response_settings_update_raid_success
    await ctx.respond(response, ensure_result=True, delete_after=int(auto_delete))
    if log_settings_changed:
        # Send to log channel
        await bot.log_from_ctx(
            ctx,
            db,
            message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_raid_success.format(
                datetime=await bot.get_timestamp(), member=ctx.member
            ),
        )
