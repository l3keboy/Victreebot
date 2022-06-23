# IMPORTS
import asyncio
import os

import hikari
import tanjun
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import DB_GUILD_LOG_SETTINGS_GENERAL_EVENTS
from utils.helpers.contants import DB_GUILD_LOG_SETTINGS_LOCATION_EVENTS
from utils.helpers.contants import DB_GUILD_LOG_SETTINGS_PROFILE_EVENTS
from utils.helpers.contants import DB_GUILD_LOG_SETTINGS_RAID_EVENTS
from utils.helpers.contants import DB_GUILD_LOG_SETTINGS_TRADE_EVENTS
from utils.helpers.contants import SUPPORTED_LANGUAGES

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
@tanjun.as_slash_command("logging", f"Update {BOT_NAME.capitalize()}'s logging settings.")
async def command_settings_update_logging(
    ctx: tanjun.abc.SlashContext,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
):
    language, auto_delete, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "is_setup"]
    )
    log_errors, *none = await db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors"])

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    timeout = 60
    embed = hikari.Embed(
        title=SUPPORTED_LANGUAGES.get(language).settings_update_logging_embed_title,
        description=SUPPORTED_LANGUAGES.get(language).settings_update_logging_embed_description,
    )

    action_row_1 = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.PRIMARY, "logs_channel")
        .set_label(SUPPORTED_LANGUAGES.get(language).settings_logging_logs_channel)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "general_events")
        .set_label(SUPPORTED_LANGUAGES.get(language).settings_logging_general_events)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "profile_events")
        .set_label(SUPPORTED_LANGUAGES.get(language).settings_logging_profile_events)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "location_events")
        .set_label(SUPPORTED_LANGUAGES.get(language).settings_logging_location_events)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "raid_events")
        .set_label(SUPPORTED_LANGUAGES.get(language).settings_logging_raid_events)
        .add_to_container()
    )
    action_row_2 = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.PRIMARY, "trade_events")
        .set_label(SUPPORTED_LANGUAGES.get(language).settings_logging_trade_events)
        .add_to_container()
    )

    response_message = await ctx.respond(embed=embed, components=[action_row_1, action_row_2])

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: event.interaction.user.id == ctx.author.id
            and event.interaction.message.id == response_message.id,
        )
    except asyncio.TimeoutError:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_settings_update_logging_failed_timeout
        await ctx.respond(response, ensure_result=True, delete_after=int(auto_delete))
        if log_errors:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_logging_failed_timeout.format(
                    datetime=await bot.get_timestamp(), member=ctx.member
                ),
            )
        return
    else:
        if event.interaction.custom_id == "logs_channel":
            await logging_configuration_logs_channel(ctx, db, bot)
            await asyncio.sleep(int(auto_delete))
        elif event.interaction.custom_id == "general_events":
            await response_message.delete()
            event, enable, timeout_cancelled = await bot.validate_enable_or_disable(ctx, "events", db)
            if not timeout_cancelled:
                await logging_configuration_events(ctx, enable, "general_events", db, bot)
            await asyncio.sleep(int(auto_delete))
        elif event.interaction.custom_id == "profile_events":
            await response_message.delete()
            event, enable, timeout_cancelled = await bot.validate_enable_or_disable(ctx, "events", db)
            if not timeout_cancelled:
                await logging_configuration_events(ctx, enable, "profile_events", db, bot)
            await asyncio.sleep(int(auto_delete))
        elif event.interaction.custom_id == "location_events":
            await response_message.delete()
            event, enable, timeout_cancelled = await bot.validate_enable_or_disable(ctx, "events", db)
            if not timeout_cancelled:
                await logging_configuration_events(ctx, enable, "location_events", db, bot)
            await asyncio.sleep(int(auto_delete))
        elif event.interaction.custom_id == "raid_events":
            await response_message.delete()
            event, enable, timeout_cancelled = await bot.validate_enable_or_disable(ctx, "events", db)
            if not timeout_cancelled:
                await logging_configuration_events(ctx, enable, "raid_events", db, bot)
            await asyncio.sleep(int(auto_delete))
        elif event.interaction.custom_id == "trade_events":
            await response_message.delete()
            event, enable, timeout_cancelled = await bot.validate_enable_or_disable(ctx, "events", db)
            if not timeout_cancelled:
                await logging_configuration_events(ctx, enable, "trade_events", db, bot)
            await asyncio.sleep(int(auto_delete))


# ------------------------------------------------------------------------- #
# Config functions #
# ------------------------------------------------------------------------- #
async def logging_configuration_logs_channel(ctx: tanjun.abc.SlashContext, db: DatabaseHandler, bot: BotUtils):
    language, auto_delete, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete"]
    )
    log_errors, log_settings_changed, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_settings_changed"]
    )

    timeout = 60
    # Send response
    embed = hikari.Embed(
        title=SUPPORTED_LANGUAGES.get(language).settings_update_logging_embed_logs_channel_title,
        description=SUPPORTED_LANGUAGES.get(language).settings_update_logging_embed_logs_channel_description,
    )

    response_message = await ctx.edit_initial_response(embed=embed, component=None)

    try:
        event = await ctx.client.events.wait_for(
            hikari.MessageCreateEvent,
            timeout=timeout,
            predicate=lambda event: event.channel_id == response_message.channel_id
            and event.author.id == ctx.author.id,
        )
    except asyncio.TimeoutError:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_settings_update_logging_failed_timeout
        await ctx.respond(response, ensure_result=True, delete_after=int(auto_delete))
        if log_errors:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_logging_failed_timeout.format(
                    datetime=await bot.get_timestamp(), member=ctx.member
                ),
            )
        return
    else:
        await event.message.delete()
        user_input = event.content.strip("<>#")
        valid_id = await bot.validate_id(user_input)
        if not valid_id:
            success = False
            return success

        try:
            channel = ctx.cache.get_guild_channel(user_input) or await ctx.rest.fetch_channel(user_input)
        except hikari.ForbiddenError:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).error_response_not_enough_permissions_for_channel
            await ctx.edit_last_response(response, embed=None, delete_after=int(auto_delete))
            if log_errors:
                # Send to log channel
                await bot.log_from_ctx(
                    ctx,
                    db,
                    message=SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_settings_update_logging_logs_channel_failed_not_enough_privileges.format(
                        datetime=await bot.get_timestamp(), member=ctx.member
                    ),
                )
            success = False
            return success

        desired_type = await bot.validate_channel_type(channel, hikari.GuildTextChannel)
        if not desired_type:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).error_response_not_a_text_channel
            await ctx.edit_last_response(response, embed=None, delete_after=int(auto_delete))
            if log_errors:
                # Send to log channel
                await bot.log_from_ctx(
                    ctx,
                    db,
                    message=SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_settings_update_logging_logs_channel_failed_not_a_text_channel.format(
                        datetime=await bot.get_timestamp(), member=ctx.member
                    ),
                )
            success = False
            return success

        success = await db.set_guild_log_setting(guild=ctx.get_guild(), parameters=[f"logs_channel_id = {channel.id}"])
        if not success:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).response_settings_update_logging_logs_channel_failed
            await ctx.edit_last_response(response, delete_after=int(auto_delete))
            if log_errors:
                # Send to log channel
                await bot.log_from_ctx(
                    ctx,
                    db,
                    message=SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_settings_update_logging_logs_channel_failed.format(
                        datetime=await bot.get_timestamp(), member=ctx.member
                    ),
                )
            success = False
            return success

        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_settings_update_logging_logs_channel_success.format(
            channel=channel.mention
        )
        await ctx.edit_last_response(response, embed=None, delete_after=int(auto_delete))
        if log_settings_changed:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(
                    language
                ).log_response_settings_update_logging_logs_channel_success.format(
                    datetime=await bot.get_timestamp(), member=ctx.member, channel=channel.mention
                ),
            )
        success = True
        return success


async def logging_configuration_events(
    ctx: tanjun.abc.SlashContext, enable: bool, event_type: str, db: DatabaseHandler, bot: BotUtils
):
    language, auto_delete, gmt, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt"]
    )
    log_errors, log_settings_changed, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_settings_changed"]
    )

    if event_type == "general_events":
        target_dict = DB_GUILD_LOG_SETTINGS_GENERAL_EVENTS
        event_type_embed = SUPPORTED_LANGUAGES.get(language).settings_logging_general_events
    if event_type == "profile_events":
        target_dict = DB_GUILD_LOG_SETTINGS_PROFILE_EVENTS
        event_type_embed = SUPPORTED_LANGUAGES.get(language).settings_logging_profile_events
    if event_type == "location_events":
        target_dict = DB_GUILD_LOG_SETTINGS_LOCATION_EVENTS
        event_type_embed = SUPPORTED_LANGUAGES.get(language).settings_logging_location_events
    if event_type == "raid_events":
        target_dict = DB_GUILD_LOG_SETTINGS_RAID_EVENTS
        event_type_embed = SUPPORTED_LANGUAGES.get(language).settings_logging_raid_events
    if event_type == "trade_events":
        target_dict = DB_GUILD_LOG_SETTINGS_TRADE_EVENTS
        event_type_embed = SUPPORTED_LANGUAGES.get(language).settings_logging_trade_events

    modules = await db.get_guild_log_settings(ctx.get_guild(), settings=[module for module in target_dict.keys()])

    modules_to_show = [list(target_dict.keys())[idx] for idx, module in enumerate(modules) if module != enable]
    if len(modules_to_show) < 1:
        await ctx.create_followup(
            SUPPORTED_LANGUAGES.get(language).error_response_settings_update_logging_events_nothing_to_change.format(
                status=SUPPORTED_LANGUAGES.get(language).enable.lower()
                if not enable
                else SUPPORTED_LANGUAGES.get(language).disable.lower()
            ),
            embed=None,
            delete_after=auto_delete,
            component=None,
        )
        success = True
        return success

    timeout = 60
    # Send response
    embed = hikari.Embed(
        title=SUPPORTED_LANGUAGES.get(language).settings_update_logging_embed_events_title,
        description=SUPPORTED_LANGUAGES.get(language).settings_update_logging_embed_events_description.format(
            status=SUPPORTED_LANGUAGES.get(language).enabled if enable else SUPPORTED_LANGUAGES.get(language).disabled
        ),
    ).add_field(
        name=SUPPORTED_LANGUAGES.get(language).settings_update_logging_embed_field_events.format(
            status=SUPPORTED_LANGUAGES.get(language).enabled.lower()
            if enable
            else SUPPORTED_LANGUAGES.get(language).disabled.lower()
        ),
        value="".join(f"\n{i+1} - {module}" for i, module in enumerate(modules_to_show)),
    )

    response_message = await ctx.create_followup(embed=embed, component=None)

    try:
        event = await ctx.client.events.wait_for(
            hikari.MessageCreateEvent,
            timeout=timeout,
            predicate=lambda event: event.channel_id == response_message.channel_id
            and event.author.id == ctx.author.id,
        )
    except asyncio.TimeoutError:
        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_settings_update_logging_failed_timeout
        await ctx.respond(response, ensure_result=True, delete_after=int(auto_delete))
        if log_errors:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_logging_failed_timeout.format(
                    datetime=await bot.get_timestamp(), member=ctx.member
                ),
            )
        return
    else:
        await response_message.delete()
        await event.message.delete()
        user_input = event.content
        user_input = user_input.replace(" ", "")
        user_input = user_input.split(",")
        try:
            user_input.remove("")
        except ValueError:
            pass

        for value in user_input:
            valid_id = await bot.validate_id(value)
            if not valid_id:
                await ctx.create_followup(
                    SUPPORTED_LANGUAGES.get(language).error_response_invalid_int_found,
                    embed=None,
                    delete_after=auto_delete,
                    component=None,
                )
                success = False
                return success

        if len(user_input) > len(modules_to_show):
            await ctx.create_followup(
                SUPPORTED_LANGUAGES.get(
                    language
                ).error_response_settings_update_logging_events_user_input_longer_than_possible_events,
                embed=None,
                delete_after=auto_delete,
                component=None,
            )
            success = False
            return success

        parameters = []
        for i, module in enumerate(modules_to_show):
            for value in user_input:
                if int(i) == int(value) - 1:
                    parameters.append(f"{module} = {enable}")

        success = await db.set_guild_log_setting(ctx.get_guild(), parameters=parameters)
        if not success:
            # Send response
            response = SUPPORTED_LANGUAGES.get(language).response_settings_update_logging_events_failed.format(
                event=event_type_embed
            )
            await ctx.create_followup(response, delete_after=int(auto_delete))
            if log_errors:
                # Send to log channel
                await bot.log_from_ctx(
                    ctx,
                    db,
                    message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_logging_events_failed.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, event=event_type_embed
                    ),
                )
            success = False
            return success

        # Send response
        response = SUPPORTED_LANGUAGES.get(language).response_settings_update_logging_events_success.format(
            event=event_type_embed
        )
        await ctx.create_followup(response, embed=None, delete_after=int(auto_delete))
        if log_settings_changed:
            # Send to log channel
            await bot.log_from_ctx(
                ctx,
                db,
                message=SUPPORTED_LANGUAGES.get(language).log_response_settings_update_logging_events_success.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, event=event_type_embed
                ),
            )
        success = True
        return success
