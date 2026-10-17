import logging

import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.exceptions import DatabaseError
from victreebot.extensions.functions.settings.commands import group
from victreebot.extensions.functions.settings.commands import subgroup
from victreebot.languages import en
from victreebot.models.GuildLogSettings import Guild_Log_SettingsUpdate

# Load command
loader = lightbulb.Loader()
loader.command(group)


# Command
@subgroup.register
class SettingsUpdateLogging(
    lightbulb.SlashCommand, 
    name="logging", 
    description="Update logging settings",
    hooks=[lightbulb.prefab.has_permissions(hikari.Permissions.MANAGE_GUILD)]
):
    """Command to update the bots logging settings."""

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context, bot: Bot) -> None:
        """Handle command interaction."""
        await ctx.defer()
        if ctx.guild_id is None:
            await ctx.respond("Command must be executed in a server.")
            return

        guild_settings = await bot.database.get_guild_settings(ctx.guild_id)
        if guild_settings is None:
            await ctx.respond("Command must be executed in a server.")
            return

        guild_log_settings = await bot.database.get_guild_log_settings(ctx.guild_id)
        if guild_log_settings is None:
            await ctx.respond("Command must be executed in a server.")
            return

        # Create language helper
        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
        auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)

        if not guild_settings.is_setup:
            response_message = await ctx.respond(language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize()))
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        auto_delete_helper = 45 if auto_delete_helper < 45 else auto_delete_helper
        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.settings_update_logging_embed_title),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.settings_update_logging_embed_description),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.settings_logging_logs_channel,
                                custom_id="settings,logs_channel",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.settings_logging_general_events,
                                custom_id="settings,general_events",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.settings_logging_profile_events,
                                custom_id="settings,profile_events",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.settings_logging_location_events,
                                custom_id="settings,location_events",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.settings_logging_raid_events,
                                custom_id="settings,raid_events",
                            ),
                        ]
                    ),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.settings_logging_trade_events,
                                custom_id="settings,trade_events",
                            ),
                        ]
                    ),
                ]
            )
        ]

        response_message = await ctx.respond(components=components)

        listening = True
        while listening:
            try:
                event = await bot.wait_for(
                    hikari.ComponentInteractionCreateEvent,
                    timeout=max(auto_delete_helper, 30),
                    predicate=lambda event: event.interaction.user.id == ctx.user.id,
                )

                command, action = event.interaction.custom_id.split(",")
                if command != "settings":
                    return

                await event.interaction.create_initial_response(6)
                if action == "logs_channel":
                    await logging_configuration_logs_channel(ctx, bot, response_message)
                if action == "general_events":
                    await bot.discord_service.delete_message(ctx.channel_id, response_message)
                    enable, timeout_cancelled = await bot.utils.validate_enable_or_disable(ctx, bot, "events")
                    if not timeout_cancelled:
                        await logging_configuration_events(ctx, bot, enable, "general_events")
                if action == "profile_events":
                    await bot.discord_service.delete_message(ctx.channel_id, response_message)
                    enable, timeout_cancelled = await bot.utils.validate_enable_or_disable(ctx, bot, "events")
                    if not timeout_cancelled:
                        await logging_configuration_events(ctx, bot, enable, "profile_events")
                if action == "location_events":
                    await bot.discord_service.delete_message(ctx.channel_id, response_message)
                    enable, timeout_cancelled = await bot.utils.validate_enable_or_disable(ctx, bot, "events")
                    if not timeout_cancelled:
                        await logging_configuration_events(ctx, bot, enable, "location_events")
                if action == "raid_events":
                    await bot.discord_service.delete_message(ctx.channel_id, response_message)
                    enable, timeout_cancelled = await bot.utils.validate_enable_or_disable(ctx, bot, "events")
                    if not timeout_cancelled:
                        await logging_configuration_events(ctx, bot, enable, "raid_events")
                if action == "trade_events":
                    await bot.discord_service.delete_message(ctx.channel_id, response_message)
                    enable, timeout_cancelled = await bot.utils.validate_enable_or_disable(ctx, bot, "events")
                    if not timeout_cancelled:
                        await logging_configuration_events(ctx, bot, enable, "trade_events")

                listening = False
            except TimeoutError:
                await ctx.delete_response(response_message)
                listening = False
            except Exception:
                logging.getLogger(__name__).exception(
                    "An error occurred while listening for the info command!"
                )
                await ctx.delete_response(response_message)
                listening = False


# ------------------------------------------------------------------------- #
# Config functions #
# ------------------------------------------------------------------------- #
async def logging_configuration_logs_channel(ctx: lightbulb.Context, bot: Bot, last_response_id: hikari.Snowflakeish):
    if ctx.guild_id is None:
        await ctx.edit_response(last_response_id, "Command must be executed in a server.")
        return

    guild_settings = await bot.database.get_guild_settings(ctx.guild_id)
    if guild_settings is None:
        await ctx.edit_response(last_response_id, "Command must be executed in a server.")
        return

    guild_log_settings = await bot.database.get_guild_log_settings(ctx.guild_id)
    if guild_log_settings is None:
        await ctx.edit_response(last_response_id, "Command must be executed in a server.")
        return

    # Create language helper
    language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
    auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)

    auto_delete_helper = 45 if auto_delete_helper < 45 else auto_delete_helper

    components = [
        hikari.impl.ContainerComponentBuilder(
            accent_color=hikari.Colour(0x8BC683),
            components=[
                hikari.impl.TextDisplayComponentBuilder(content=language_helper.settings_update_logging_embed_logs_channel_title),
                hikari.impl.TextDisplayComponentBuilder(content=language_helper.settings_update_logging_embed_logs_channel_description),
            ]
        )
    ]

    await ctx.edit_response(last_response_id, components=components)

    listening = True
    while listening:
        try:
            event = await bot.wait_for(
                hikari.MessageCreateEvent,
                timeout=max(auto_delete_helper, 30),
                predicate=lambda event: event.channel_id == ctx.channel_id and event.author_id == ctx.user.id,
            )

            await event.message.delete()

            user_input = None
            if event.content:
                user_input = event.content.strip("<>#")

            if not user_input:
                success = False
                return success

            valid_id = await bot.utils.validate_id(user_input)
            if not valid_id:
                success = False
                return success

            channel = bot.cache.get_guild_channel(int(user_input)) or await bot.discord_service.get_guild_channel(int(user_input))
            if not channel:
                success = False
                components_channel_failed = [
                    hikari.impl.ContainerComponentBuilder(
                        accent_color=hikari.Colour(0x8BC683),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_settings_update_logging_failed),
                        ]
                    )
                ]
                await ctx.edit_response(last_response_id, components=components_channel_failed)
                await bot.utils.handle_auto_delete(ctx.channel_id, last_response_id, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_settings_update_logging_failed.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return success

            desired_type = await bot.utils.validate_channel_type(channel, hikari.GuildTextChannel) # type: ignore
            if not desired_type:
                success = False
                components_type_failed = [
                    hikari.impl.ContainerComponentBuilder(
                        accent_color=hikari.Colour(0x8BC683),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(content=language_helper.error_response_not_a_text_channel),
                        ]
                    )
                ]
                await ctx.edit_response(last_response_id, components=components_type_failed)
                await bot.utils.handle_auto_delete(ctx.channel_id, last_response_id, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_settings_update_logging_logs_channel_failed_not_a_text_channel.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return success

            new_guild_log_settings = Guild_Log_SettingsUpdate(guild_id=ctx.guild_id, logs_channel_id=channel.id)
         
            try:
                guild_log_settings = await bot.database.change_guild_log_settings(guild_log_settings, new_guild_log_settings)
            except DatabaseError:
                components_db_error = [
                    hikari.impl.ContainerComponentBuilder(
                        accent_color=hikari.Colour(0x8BC683),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_settings_update_logging_logs_channel_failed),
                        ]
                    )
                ]
                await ctx.edit_response(last_response_id, components=components_db_error)
                await bot.utils.handle_auto_delete(ctx.channel_id, last_response_id, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_settings_update_logging_logs_channel_failed.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                raise

            components_success = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_settings_update_logging_logs_channel_success.format(channel=channel.mention)),
                    ]
                )
            ]
            await ctx.edit_response(last_response_id, components=components_success)
            await bot.utils.handle_auto_delete(ctx.channel_id, last_response_id, auto_delete_helper)
            if guild_log_settings.log_settings_changed:
                log_response = language_helper.log_response_settings_update_logging_logs_channel_success.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member, channel=channel.mention
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response) 

            listening = False
        except TimeoutError:
            await ctx.delete_response(last_response_id)
            listening = False
        except Exception:
            logging.getLogger(__name__).exception(
                "An error occurred while listening for the info command!"
            )
            await ctx.delete_response(last_response_id)
            listening = False


async def logging_configuration_events(ctx: lightbulb.Context, bot: Bot, enable: bool, event_type: str):
    if ctx.guild_id is None:
        return

    guild_settings = await bot.database.get_guild_settings(ctx.guild_id)
    if guild_settings is None:
        return

    guild_log_settings = await bot.database.get_guild_log_settings(ctx.guild_id)
    if guild_log_settings is None:
        return

    # Create language helper
    language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
    auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)

    target_dict: dict[str, bool] = {}
    event_type_embed: str = ""
    if event_type == "general_events":
        target_dict = {
            "log_errors": guild_log_settings.log_errors, 
            "log_info": guild_log_settings.log_info, 
            "log_settings_changed": guild_log_settings.log_settings_changed
        }
        event_type_embed = language_helper.settings_logging_general_events
    if event_type == "profile_events":
        target_dict = {
            "log_profile_edit": guild_log_settings.log_profile_edit, 
            "log_profile_view": guild_log_settings.log_profile_view, 
        }
        event_type_embed = language_helper.settings_logging_profile_events
    if event_type == "location_events":
        target_dict = {
            "log_location_add": guild_log_settings.log_location_add, 
            "log_location_delete": guild_log_settings.log_location_delete, 
            "log_location_edit": guild_log_settings.log_location_edit, 
            "log_location_info": guild_log_settings.log_location_info, 
            "log_location_list": guild_log_settings.log_location_list, 
        }
        event_type_embed = language_helper.settings_logging_location_events
    if event_type == "raid_events":
        target_dict = {
            "log_raid_create": guild_log_settings.log_raid_create, 
            "log_raid_delete": guild_log_settings.log_raid_delete, 
            "log_raid_edit": guild_log_settings.log_raid_edit, 
        }
        event_type_embed = language_helper.settings_logging_raid_events
    if event_type == "trade_events":
        target_dict = {
            "log_trade_offer": guild_log_settings.log_trade_offer, 
            "log_trade_proposal": guild_log_settings.log_trade_proposal, 
            "log_trade_search": guild_log_settings.log_trade_search, 
        }
        event_type_embed = language_helper.settings_logging_trade_events

    modules_to_show = [
        key for key, value in target_dict.items()
        if value != enable
    ]
    if len(modules_to_show) <= 0:
        components_id_failed = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.error_response_settings_update_logging_events_nothing_to_change.format(
                        status=language_helper.enable.lower()
                        if enable
                        else language_helper.disable.lower()
                    )),
                ]
            )
        ]
        last_response_id = await ctx.respond(components=components_id_failed)
        await bot.utils.handle_auto_delete(ctx.channel_id, last_response_id, auto_delete_helper)
        if guild_log_settings.log_errors:
            log_response = language_helper.log_response_settings_update_logging_events_failed.format(
                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member, event=event_type_embed
            )
            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
        return

    auto_delete_helper = 60 if auto_delete_helper < 60 else auto_delete_helper

    components = [
        hikari.impl.ContainerComponentBuilder(
            accent_color=hikari.Colour(0x8BC683),
            components=[
                hikari.impl.TextDisplayComponentBuilder(content=language_helper.settings_update_logging_embed_events_title),
                hikari.impl.TextDisplayComponentBuilder(content=language_helper.settings_update_logging_embed_events_description.format(
                    status=language_helper.enabled if enable else language_helper.disabled
                )),
                hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                hikari.impl.TextDisplayComponentBuilder(content=language_helper.settings_update_logging_embed_field_events.format(
                    status=language_helper.enabled.lower()
                    if enable
                    else language_helper.disabled.lower()
                )),
                hikari.impl.TextDisplayComponentBuilder(content="".join(f"\n{i+1} - {module}" for i, module in enumerate(modules_to_show))),
            ]
        )
    ]

    last_response_id = await ctx.respond(components=components)

    listening = True
    while listening:
        try:
            event = await bot.wait_for(
                hikari.MessageCreateEvent,
                timeout=max(auto_delete_helper, 30),
                predicate=lambda event: event.channel_id == ctx.channel_id and event.author_id == ctx.user.id,
            )

            await event.message.delete()

            user_input = event.content
            if not user_input:
                return
            
            user_input = user_input.replace(" ", "")
            user_input = user_input.split(",")
            try:
                user_input.remove("")
            except ValueError:
                pass

            for value in user_input:
                valid_id = await bot.utils.validate_id(value)
                if not valid_id:
                    success = False
                    components_id_failed = [
                        hikari.impl.ContainerComponentBuilder(
                            accent_color=hikari.Colour(0x8BC683),
                            components=[
                                hikari.impl.TextDisplayComponentBuilder(content=language_helper.error_response_invalid_int_found),
                            ]
                        )
                    ]
                    await ctx.edit_response(last_response_id, components=components_id_failed)
                    await bot.utils.handle_auto_delete(ctx.channel_id, last_response_id, auto_delete_helper)
                    if guild_log_settings.log_errors:
                        log_response = language_helper.log_response_settings_update_logging_events_failed.format(
                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                        )
                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                    return success

            if len(user_input) > len(modules_to_show):
                success = False
                components_length_failed = [
                    hikari.impl.ContainerComponentBuilder(
                        accent_color=hikari.Colour(0x8BC683),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(content=language_helper.error_response_settings_update_logging_events_user_input_longer_than_possible_events),
                        ]
                    )
                ]
                await ctx.edit_response(last_response_id, components=components_length_failed)
                await bot.utils.handle_auto_delete(ctx.channel_id, last_response_id, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_settings_update_logging_events_failed.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return success

            new_guild_log_settings = Guild_Log_SettingsUpdate(guild_id=ctx.guild_id)
            for i, module in enumerate(modules_to_show):
                for value in user_input:
                    if int(i) == int(value) - 1:
                        setattr(new_guild_log_settings, module, enable)

            try:
                guild_log_settings = await bot.database.change_guild_log_settings(guild_log_settings, new_guild_log_settings)
            except DatabaseError:
                components_db_error = [
                    hikari.impl.ContainerComponentBuilder(
                        accent_color=hikari.Colour(0x8BC683),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_settings_update_logging_events_failed),
                        ]
                    )
                ]
                await ctx.edit_response(last_response_id, components=components_db_error)
                await bot.utils.handle_auto_delete(ctx.channel_id, last_response_id, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_settings_update_logging_events_failed.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member, event=event_type_embed
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                raise

            components_success = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_settings_update_logging_events_success.format(event=event_type_embed)),
                    ]
                )
            ]
            await ctx.edit_response(last_response_id, components=components_success)
            await bot.utils.handle_auto_delete(ctx.channel_id, last_response_id, auto_delete_helper)
            if guild_log_settings.log_settings_changed:
                log_response = language_helper.log_response_settings_update_logging_events_success.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member, event=event_type_embed
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response) 

            listening = False
        except TimeoutError:
            await ctx.delete_response(last_response_id)
            listening = False
        except Exception:
            logging.getLogger(__name__).exception(
                "An error occurred while listening for the info command!"
            )
            await ctx.delete_response(last_response_id)
            listening = False