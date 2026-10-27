# Copyright (c) 2022-present l3keboy

import datetime
import logging
import time
import zoneinfo

import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.contants import SUPPORTED_LOCATION_TYPES
from victreebot.contants import SUPPORTED_RAID_TYPES
from victreebot.core.bot import Bot
from victreebot.extensions.functions.raids.autocomplete.autocomplete_raid_id import autocomplete_raid_id
from victreebot.extensions.functions.raids.commands import group
from victreebot.extensions.functions.raids.menus.time_menu import TimeModal
from victreebot.languages import en
from victreebot.utils.shared_autocompletes import autocomplete_locations
from victreebot.utils.shared_autocompletes import autocomplete_pokemon

# Load command
loader = lightbulb.Loader()
loader.command(group)


# Command
@group.register
class RaidsEdit(lightbulb.SlashCommand, name="edit", description="Edit an existing raid"):
    """Command to delete a raid."""

    raid_id: str = lightbulb.string(
        "raid_id",
        "The ID of the raid to edit",
        autocomplete=autocomplete_raid_id,  # type: ignore[arg-type]  # mypy: ignore
    )
    new_boss: str | None = lightbulb.string(
        "new_boss",
        "The new boss to fight (leave empty for no change!)",
        autocomplete=autocomplete_pokemon,  # type: ignore[arg-type]  # mypy: ignore
        default=None,
    )
    new_location: str | None = lightbulb.string(
        "new_location",
        "The new location (leave empty for no change!)",
        autocomplete=autocomplete_locations,  # type: ignore[arg-type]  # mypy: ignore
        default=None,
    )
    new_raid_type: str | None = lightbulb.string(
        "new_raid_type",
        "Change the raid type",
        choices=[lightbulb.Choice(name=raid_type, value=raid_type) for raid_type in SUPPORTED_RAID_TYPES],
        default=None,
    )
    change_date_time: str | None = lightbulb.string(
        "change_date_time",
        "The the date and time of a raid (Leave empty or no for no change)",
        choices=[lightbulb.Choice(name="Yes", value="Yes"), lightbulb.Choice(name="No", value="No")],
        default=None,
    )

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

        guild_stats = await bot.database.get_guild_stats(ctx.guild_id)
        if guild_stats is None:
            await ctx.respond("Command must be executed in a server.")
            return

        # Create language helper
        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
        auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)
        response_message: hikari.Snowflakeish | None = None

        if not guild_settings.is_setup:
            response_message = await ctx.respond(
                language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize())
            )
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        raid = bot.raids.get(self.raid_id)
        if raid is None:
            response_message = await ctx.respond(
                language_helper.response_raid_edit_no_raid_found, components=[], embeds=[]
            )
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_raid_edit_no_raid_found.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        if ctx.user.id != raid.raid_creator_id and (
            ctx.member is not None and guild_settings.moderator_role_id not in ctx.member.role_ids
        ):
            response_message = await ctx.respond(
                language_helper.response_raid_edit_not_creator_or_moderator.format(
                    bot_name=bot.vars.BOT_NAME.capitalize()
                ),
                components=[],
                embeds=[],
            )
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_raid_edit_not_creator_or_moderator.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                    member=ctx.member,
                    bot_name=bot.vars.BOT_NAME.capitalize(),
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        auto_delete_helper = max(auto_delete_helper, 120)

        # Handle new boss
        if self.new_boss is not None and (self.new_boss not in {"egg1", "egg3", "egg5", "eggmega"}):
            success, pokemon, pokemon_image = await bot.utils.validate_pokemon(self.new_boss)
            if not success or not pokemon or not pokemon_image:
                components = [
                    hikari.impl.ContainerComponentBuilder(
                        accent_color=hikari.Colour(0x8BC683),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(
                                content=language_helper.response_raid_edit_unknown_boss
                            )
                        ],
                    )
                ]
                if response_message:
                    await ctx.edit_response(response_message, components=components)
                else:
                    response_message = await ctx.respond(components=components, embeds=[])
                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_raid_edit_unknown_boss.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return

        # Handle new location
        location_name = None
        location_type = None
        if self.new_location is not None:
            location_splitted = self.new_location.split(",")
            if len(location_splitted) == 1:
                location_name = location_splitted[0].replace("'", "''")
                location_name = f"{location_name}"

                components = [
                    hikari.impl.ContainerComponentBuilder(
                        accent_color=hikari.Colour(0x8BC683),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(
                                content=language_helper.raid_create_embed_title_location_type
                            ),
                            hikari.impl.TextDisplayComponentBuilder(
                                content=language_helper.raid_create_embed_description_location_type
                            ),
                            hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                            hikari.impl.MessageActionRowBuilder(
                                components=[
                                    hikari.impl.InteractiveButtonBuilder(
                                        style=hikari.ButtonStyle.PRIMARY,
                                        label=location_type,
                                        custom_id=f"raids,{location_type.lower()}",
                                    )
                                    for location_type in SUPPORTED_LOCATION_TYPES
                                ]
                            ),
                        ],
                    )
                ]
                if response_message:
                    await ctx.edit_response(response_message, components=components)
                else:
                    response_message = await ctx.respond(components=components, embeds=[])

                listening = True
                while listening:
                    try:
                        event = await bot.wait_for(
                            hikari.ComponentInteractionCreateEvent,
                            timeout=max(auto_delete_helper, 30),
                            predicate=lambda event: event.interaction.user.id == ctx.user.id,
                        )

                        command, action = event.interaction.custom_id.split(",")
                        if command != "raids":
                            return

                        await event.interaction.create_initial_response(6)
                        location_type = action

                        listening = False
                    except TimeoutError:
                        await ctx.delete_response(response_message)
                        listening = False
                    except Exception:
                        logging.getLogger(__name__).exception(
                            "An error occurred while listening for the raids command!"
                        )
                        await ctx.delete_response(response_message)
                        listening = False
            else:
                location_name = location_splitted[1].removeprefix(" ")
                location_name = location_name.replace("'", "''")
                location_name = f"{location_name}"
                location_type = f"'{location_splitted[0]}'"

        if self.new_location is None:
            location_name = None
            location_type = None

        end_time = None
        raid_takes_place_at_to_show = None
        raid_takes_place_at = None

        if self.change_date_time is not None and self.change_date_time != "No":
            timezone = zoneinfo.ZoneInfo(guild_settings.gmt)

            timezone_aware_current_date = datetime.datetime.today().astimezone(timezone).date()
            days = [timezone_aware_current_date + datetime.timedelta(days=offset) for offset in range(24)]

            components = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.raid_create_embed_title_date),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.raid_create_embed_description_date
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.MessageActionRowBuilder(
                            components=[
                                hikari.impl.TextSelectMenuBuilder(
                                    custom_id="raids,date",
                                    min_values=1,
                                    max_values=1,
                                    options=[
                                        hikari.impl.SelectOptionBuilder(
                                            label=(
                                                f"{language_helper.weekdays[day.weekday()]} {day.day} "
                                                f"{language_helper.months[day.month - 1]}"
                                            ),
                                            value=day.isoformat(),
                                        )
                                        for day in days[:24]
                                    ],
                                )
                            ]
                        ),
                    ],
                )
            ]

            if response_message:
                await ctx.edit_response(response_message, components=components)
            else:
                response_message = await ctx.respond(components=components, embeds=[])

            listening = True
            raid_date = ""
            raid_time = ""
            while listening:
                try:
                    event = await bot.wait_for(
                        hikari.ComponentInteractionCreateEvent,
                        timeout=max(auto_delete_helper, 30),
                        predicate=lambda event: event.interaction.user.id == ctx.user.id,
                    )

                    command, action = event.interaction.custom_id.split(",")
                    if command != "raids":
                        return

                    raid_date = event.interaction.values[0]

                    # Time modal popup
                    time_modal = TimeModal(guild_settings.language)
                    await event.interaction.create_modal_response(
                        language_helper.raid_create_modal_time, "_get_raid_time", components=time_modal
                    )

                    try:
                        await time_modal.attach(bot.client, "_get_raid_time", timeout=auto_delete_helper)
                    except TimeoutError:
                        await ctx.delete_response(response_message)
                        listening = False
                    else:
                        if time_modal.selected_btn == "_get_raid_time" and (time_modal.given_time is not None):
                            raid_time = time_modal.given_time
                            valid_time = await bot.utils.validate_timestamp_format(raid_time, "%H:%M")
                            if not valid_time:
                                components_invalid_time = [
                                    hikari.impl.ContainerComponentBuilder(
                                        accent_color=hikari.Colour(0x8BC683),
                                        components=[
                                            hikari.impl.TextDisplayComponentBuilder(
                                                content=language_helper.response_raid_create_invalid_time
                                            )
                                        ],
                                    )
                                ]
                                await ctx.edit_response(response_message, embeds=[], components=components_invalid_time)
                                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                                if guild_log_settings.log_errors:
                                    log_response = language_helper.log_response_raid_create_invalid_time.format(
                                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                        member=ctx.member,
                                    )
                                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                                return

                    listening = False
                except TimeoutError:
                    await ctx.delete_response(response_message)
                    listening = False
                except Exception:
                    logging.getLogger(__name__).exception("An error occurred while listening for the raids command!")
                    await ctx.delete_response(response_message)
                    listening = False

            raid_date = await bot.utils.change_timestamp_format(raid_date, "%Y-%m-%d", "%d/%m/%Y")
            raid_takes_place_at = f"{raid_date} {raid_time}"

            if guild_settings.extended_time_format:
                raid_takes_place_at_to_show = f"{raid_date} {raid_time} {guild_settings.gmt}"
            else:
                raid_takes_place_at_to_show = f"{raid_time}"

            raid_takes_place_at_server_timezone_aware = datetime.datetime.strptime(
                str(raid_takes_place_at), "%d/%m/%Y %H:%M"
            ).replace(tzinfo=timezone)
            datetime_obj_now_utc = datetime.datetime.now().astimezone(tz=zoneinfo.ZoneInfo("UTC"))
            datetime_obj_raid_takes_place_at_utc = raid_takes_place_at_server_timezone_aware.astimezone(
                tz=zoneinfo.ZoneInfo("UTC")
            )

            if datetime_obj_raid_takes_place_at_utc < datetime_obj_now_utc:
                components_date_passed = [
                    hikari.impl.ContainerComponentBuilder(
                        accent_color=hikari.Colour(0x8BC683),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(
                                content=language_helper.response_raid_create_date_time_already_past
                            )
                        ],
                    )
                ]
                await ctx.edit_response(response_message, embeds=[], components=components_date_passed)
                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_raid_create_date_time_already_past.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return

            difference = datetime_obj_raid_takes_place_at_utc - datetime_obj_now_utc
            end_time = time.time() + difference.total_seconds() + int(guild_settings.raid_timeout)

        success = await raid.update_raid(
            new_boss=self.new_boss,
            new_location=location_name,
            new_location_type=location_type,
            new_type=self.new_raid_type,
            new_end_time=int(end_time) if end_time else None,
            new_raid_takes_place_at_to_show=raid_takes_place_at_to_show,
            new_raid_takes_place_at=raid_takes_place_at,
        )
        if not success:
            components = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_raid_edit_failed)
                    ],
                )
            ]
            if response_message:
                await ctx.edit_response(response_message, components=components)
            else:
                response_message = await ctx.respond(components=components, embeds=[])
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_raid_edit_failed.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_raid_edit)],
            )
        ]
        if response_message:
            await ctx.edit_response(response_message, components=components)
        else:
            response_message = await ctx.respond(components=components, embeds=[])
        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
        if guild_log_settings.log_raid_edit:
            log_response = language_helper.log_response_raid_edit.format(
                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
            )
            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
