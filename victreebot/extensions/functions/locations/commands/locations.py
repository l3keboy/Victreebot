# Copyright (c) 2022-present l3keboy

import logging
import math

import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.exceptions import DatabaseError
from victreebot.extensions.functions.locations.menus.location_description_menu import LocationDescriptionModal
from victreebot.extensions.functions.locations.menus.location_long_lat_menu import LocationLongLatModal
from victreebot.extensions.functions.locations.menus.location_name_menu import LocationNameModal
from victreebot.languages import en
from victreebot.models.Locations import LocationsUpdate

LOCATION_AUTO_DELETE_THRESHOLD = 5

# Load command
loader = lightbulb.Loader()


# Command
@loader.command
class Locations(lightbulb.SlashCommand, name="locations", description="Interactions for locations"):
    """Command to get info about a pokemon."""

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
            response_message = await ctx.respond(
                language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize())
            )
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        auto_delete_helper = max(auto_delete_helper, 120)

        components_home = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.location_embed_title),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.location_embed_description),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.SUCCESS,
                                label=language_helper.location_action_row_add_gym,
                                custom_id="locations,add_gym",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.DANGER,
                                label=language_helper.location_action_row_delete_gym,
                                custom_id="locations,delete_gym",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.location_action_row_edit_gym,
                                custom_id="locations,edit_gym",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.location_action_row_list_gym,
                                custom_id="locations,list_gyms",
                            ),
                        ]
                    ),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.SUCCESS,
                                label=language_helper.location_action_row_add_pokestop,
                                custom_id="locations,add_pokestop",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.DANGER,
                                label=language_helper.location_action_row_delete_pokestop,
                                custom_id="locations,delete_pokestop",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.location_action_row_edit_pokestop,
                                custom_id="locations,edit_pokestop",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=language_helper.location_action_row_list_pokestop,
                                custom_id="locations,list_pokestops",
                            ),
                        ]
                    ),
                ],
            )
        ]

        response_message = await ctx.respond(components=components_home)

        listening = True
        while listening:
            try:
                event = await bot.wait_for(
                    hikari.ComponentInteractionCreateEvent,
                    timeout=max(auto_delete_helper, 30),
                    predicate=lambda event: event.interaction.user.id == ctx.user.id,
                )

                command, action = event.interaction.custom_id.split(",")
                if command != "locations":
                    return

                await bot.discord_service.delete_message(ctx.channel_id, response_message)
                if action in {"list_gyms", "list_pokestops"}:
                    await event.interaction.create_initial_response(6)
                    location_type = "gym" if action == "list_gyms" else "pokéstop"
                    locations = await bot.database.get_locations_by_type(ctx.guild_id, location_type)
                    if len(locations) <= 0:
                        response_message = await ctx.respond(
                            language_helper.response_location_list_no_results.format(
                                location_type=location_type.strip("'")
                            )
                        )
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_list_no_results.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                member=ctx.member,
                                location_type=location_type.strip("'"),
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        return

                    all_locations = [location.name for location in locations]
                    if guild_log_settings.log_errors:
                        log_response = language_helper.log_response_location_list_requested.format(
                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                            member=ctx.member,
                            location_type=location_type.strip("'"),
                        )
                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                    components: list[tuple[hikari.impl.ContainerComponentBuilder]] = []
                    if len(all_locations) < LOCATION_AUTO_DELETE_THRESHOLD:
                        auto_delete_helper = max(auto_delete_helper, 20)

                        known_coordinates = (
                            "[{google_maps_translation}](https://www.google.com/maps/place/{latitude},{longitude})"
                        )
                        unknown_coordinates = f"`{language_helper.location_no_coordinates_set}`"

                        components.append(
                            (
                                hikari.impl.ContainerComponentBuilder(
                                    accent_color=hikari.Colour(0x8BC683),
                                    components=[
                                        hikari.impl.TextDisplayComponentBuilder(
                                            content=language_helper.location_list_embed_title
                                        ),
                                        hikari.impl.TextDisplayComponentBuilder(
                                            content=language_helper.location_list_embed_description.format(
                                                location_type=location_type.strip("'")
                                            )
                                        ),
                                        hikari.impl.SeparatorComponentBuilder(
                                            divider=True, spacing=hikari.SpacingType.LARGE
                                        ),
                                        hikari.impl.TextDisplayComponentBuilder(
                                            content=language_helper.location_list_embed_field_locations
                                        ),
                                        hikari.impl.TextDisplayComponentBuilder(
                                            content="\n".join(
                                                f"***{location.name}***"
                                                " \n"
                                                f"{known_coordinates.format(google_maps_translation=language_helper.location_google_maps, latitude=location.latitude, longitude=location.longitude) if location.latitude is not None and location.longitude is not None else unknown_coordinates}"  # noqa: E501
                                                for location in locations
                                            )
                                        ),
                                    ],
                                ),
                            )
                        )
                        await self._handle_listening(components, ctx, bot, auto_delete_helper)
                    else:
                        auto_delete_helper = max(auto_delete_helper, 45)

                        i, start, end, max_length = 1, 0, 5, 5
                        pages = math.ceil(len(locations) / max_length)

                        known_coordinates = (
                            "[{google_maps_translation}](https://www.google.com/maps/place/{latitude},{longitude})"
                        )
                        unknown_coordinates = f"`{language_helper.location_no_coordinates_set}`"

                        while i <= pages:
                            components.append(
                                (
                                    hikari.impl.ContainerComponentBuilder(
                                        accent_color=hikari.Colour(0x8BC683),
                                        components=[
                                            hikari.impl.TextDisplayComponentBuilder(
                                                content=language_helper.location_list_embed_title
                                            ),
                                            hikari.impl.TextDisplayComponentBuilder(
                                                content=language_helper.location_list_embed_description.format(
                                                    location_type=location_type.strip("'")
                                                )
                                            ),
                                            hikari.impl.SeparatorComponentBuilder(
                                                divider=True, spacing=hikari.SpacingType.LARGE
                                            ),
                                            hikari.impl.TextDisplayComponentBuilder(
                                                content=language_helper.location_list_embed_field_locations
                                            ),
                                            hikari.impl.TextDisplayComponentBuilder(
                                                content="\n".join(
                                                    f"***{location.name}***"
                                                    " \n"
                                                    f"{known_coordinates.format(google_maps_translation=language_helper.location_google_maps, latitude=location.latitude, longitude=location.longitude) if location.latitude is not None and location.longitude is not None else unknown_coordinates}"  # noqa: E501
                                                    for location in locations[start:end]
                                                )
                                            ),
                                        ],
                                    ),
                                )
                            )
                            start += 5
                            end += 5
                            i += 1

                        components = await self._add_pagination_to_components(components)
                        await self._handle_listening(components, ctx, bot, auto_delete_helper)

                if action in {"add_gym", "add_pokestop"}:
                    location_type = "gym" if action == "add_gym" else "pokéstop"
                    success, location_name = await self._get_location_name(ctx, event, bot, location_type)
                    if not success:
                        response_message = await ctx.respond(language_helper.response_location_add_failed)
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_add_failed.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                member=ctx.member,
                                location_type=location_type,
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        return

                    location_exists = await bot.database.get_location(ctx.guild_id, location_type, location_name)
                    if location_exists:
                        response_message = await ctx.respond(
                            language_helper.response_location_add_failed_already_exists.format(
                                location_type=location_type.strip("'")
                            )
                        )
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_add_failed_already_exists.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                member=ctx.member,
                                location_type=location_type.strip("'"),
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        return

                    event, add = await bot.utils.validate_add_or_no_add(ctx, bot, "a description")
                    if not event:
                        response_message = await ctx.respond(language_helper.response_location_add_failed)
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_add_failed.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                member=ctx.member,
                                location_type=location_type,
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        return

                    location_description = None
                    if add:
                        success, location_description = await self._get_location_description(
                            ctx, event, bot, location_type
                        )
                        if not success:
                            response_message = await ctx.respond(language_helper.response_location_add_failed)
                            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                            if guild_log_settings.log_errors:
                                log_response = language_helper.log_response_location_add_failed.format(
                                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                    member=ctx.member,
                                    location_type=location_type,
                                )
                                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                            return

                    event, add = await bot.utils.validate_add_or_no_add(ctx, bot, "the latitude and longitude")
                    if not event:
                        response_message = await ctx.respond(language_helper.response_location_add_failed)
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_add_failed.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                member=ctx.member,
                                location_type=location_type,
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        return

                    latitude, longitude = None, None
                    if add:
                        success, longitude, latitude = await self._get_location_long_lat(ctx, event, bot, location_type)
                        if not success:
                            response_message = await ctx.respond(language_helper.response_location_add_failed)
                            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                            if guild_log_settings.log_errors:
                                log_response = language_helper.log_response_location_add_failed.format(
                                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                    member=ctx.member,
                                    location_type=location_type,
                                )
                                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                            return

                    try:
                        _ = await bot.database.insert_location(
                            ctx.guild_id, location_type, location_name, latitude, longitude, location_description
                        )
                    except DatabaseError:
                        response_message = await ctx.respond(language_helper.response_location_add_failed)
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_add_failed.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                member=ctx.member,
                                location_type=location_type,
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        raise

                    response_message = await ctx.respond(language_helper.response_location_add_success)
                    await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                    if guild_log_settings.log_location_add:
                        log_response = language_helper.log_response_location_add_success.format(
                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                            member=ctx.member,
                            location_type=location_type,
                        )
                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                if action in {"delete_gym", "delete_pokestop"}:
                    location_type = "gym" if action == "delete_gym" else "pokéstop"
                    success, location_name = await self._get_location_name(ctx, event, bot, location_type)
                    if not success:
                        response_message = await ctx.respond(language_helper.response_location_delete_failed)
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_delete_failed.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        return

                    location_exists = await bot.database.get_location(ctx.guild_id, location_type, location_name)
                    if not location_exists:
                        response_message = await ctx.respond(
                            language_helper.response_location_delete_failed_no_such_location.format(
                                location_type=location_type.strip("'")
                            )
                        )
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_delete_failed_no_such_location.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                member=ctx.member,
                                location_type=location_type.strip("'"),
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        return

                    try:
                        await bot.database.delete_location(location_exists)
                    except DatabaseError:
                        response_message = await ctx.respond(
                            language_helper.response_location_delete_failed.format(
                                location_type=location_type.strip("'")
                            )
                        )
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_delete_failed.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                member=ctx.member,
                                location_type=location_type.strip("'"),
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        raise

                    response_message = await ctx.respond(
                        language_helper.response_location_delete_success.format(location_type=location_type.strip("'"))
                    )
                    await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                    if guild_log_settings.log_location_delete:
                        log_response = language_helper.log_response_location_delete_success.format(
                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                            member=ctx.member,
                            location_type=location_type.strip("'"),
                        )
                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                if action in {"edit_gym", "edit_pokestop"}:
                    location_type = "gym" if action == "edit_gym" else "pokéstop"
                    success, location_name = await self._get_location_name(ctx, event, bot, location_type)
                    if not success:
                        response_message = await ctx.respond(language_helper.response_location_edit_failed)
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_edit_failed.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        return

                    location_exists = await bot.database.get_location(ctx.guild_id, location_type, location_name)
                    if not location_exists:
                        response_message = await ctx.respond(
                            language_helper.response_location_edit_failed_no_such_location.format(
                                location_type=location_type.strip("'")
                            )
                        )
                        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                        if guild_log_settings.log_errors:
                            log_response = language_helper.log_response_location_edit_failed_no_such_location.format(
                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                member=ctx.member,
                                location_type=location_type.strip("'"),
                            )
                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                        return

                    components_home = [
                        hikari.impl.ContainerComponentBuilder(
                            accent_color=hikari.Colour(0x8BC683),
                            components=[
                                hikari.impl.TextDisplayComponentBuilder(content=language_helper.location_embed_title),
                                hikari.impl.TextDisplayComponentBuilder(
                                    content=language_helper.location_embed_description
                                ),
                                hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                                hikari.impl.MessageActionRowBuilder(
                                    components=[
                                        hikari.impl.InteractiveButtonBuilder(
                                            style=hikari.ButtonStyle.PRIMARY,
                                            label=language_helper.location_action_row_edit_description,
                                            custom_id="locations,location_description",
                                        ),
                                        hikari.impl.InteractiveButtonBuilder(
                                            style=hikari.ButtonStyle.PRIMARY,
                                            label=language_helper.location_action_row_edit_latitude_longitude,
                                            custom_id="locations,location_latitude_longitude",
                                        ),
                                    ]
                                ),
                            ],
                        )
                    ]

                    response_message_edit = await ctx.respond(components=components_home)

                    listening = True
                    while listening:
                        try:
                            event_edit = await bot.wait_for(
                                hikari.ComponentInteractionCreateEvent,
                                timeout=max(auto_delete_helper, 30),
                                predicate=lambda event: event.interaction.user.id == ctx.user.id,
                            )

                            command, action = event_edit.interaction.custom_id.split(",")
                            if command != "locations":
                                return

                            await bot.discord_service.delete_message(ctx.channel_id, response_message_edit)

                            if action == "location_description":
                                event_edit_description, add = await bot.utils.validate_add_or_no_add(
                                    ctx, bot, "a description"
                                )
                                if not event_edit_description:
                                    response_message = await ctx.respond(language_helper.response_location_edit_failed)
                                    await bot.utils.handle_auto_delete(
                                        ctx.channel_id, response_message, auto_delete_helper
                                    )
                                    if guild_log_settings.log_errors:
                                        log_response = language_helper.log_response_location_edit_failed.format(
                                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                            member=ctx.member,
                                            location_type=location_type,
                                        )
                                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                                    return

                                location_description = None
                                if add:
                                    success, location_description = await self._get_location_description(
                                        ctx, event_edit_description, bot, location_type
                                    )
                                    if not success:
                                        response_message = await ctx.respond(
                                            language_helper.response_location_edit_failed
                                        )
                                        await bot.utils.handle_auto_delete(
                                            ctx.channel_id, response_message, auto_delete_helper
                                        )
                                        if guild_log_settings.log_errors:
                                            log_response = language_helper.log_response_location_edit_failed.format(
                                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                                member=ctx.member,
                                                location_type=location_type,
                                            )
                                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                                        return

                                new_location = LocationsUpdate(guild_id=ctx.guild_id, description=location_description)

                                try:
                                    _ = await bot.database.change_location(location_exists, new_location)
                                except DatabaseError:
                                    response_message = await ctx.respond(language_helper.response_location_edit_failed)
                                    await bot.utils.handle_auto_delete(
                                        ctx.channel_id, response_message, auto_delete_helper
                                    )
                                    if guild_log_settings.log_errors:
                                        log_response = language_helper.log_response_location_edit_failed.format(
                                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                            member=ctx.member,
                                            location_type=location_type,
                                        )
                                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                                    raise

                                response_message = await ctx.respond(language_helper.response_location_edit_success)
                                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                                if guild_log_settings.log_location_add:
                                    log_response = language_helper.log_response_location_edit_success.format(
                                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                        member=ctx.member,
                                        location_type=location_type,
                                    )
                                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                            if action == "location_latitude_longitude":
                                event_edit_long_lat, add = await bot.utils.validate_add_or_no_add(
                                    ctx, bot, "the latitude and longitude"
                                )
                                if not event_edit_long_lat:
                                    response_message = await ctx.respond(language_helper.response_location_edit_failed)
                                    await bot.utils.handle_auto_delete(
                                        ctx.channel_id, response_message, auto_delete_helper
                                    )
                                    if guild_log_settings.log_errors:
                                        log_response = language_helper.log_response_location_edit_failed.format(
                                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                            member=ctx.member,
                                            location_type=location_type,
                                        )
                                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                                    return

                                latitude, longitude = None, None
                                if add:
                                    success, longitude, latitude = await self._get_location_long_lat(
                                        ctx, event_edit_long_lat, bot, location_type
                                    )
                                    if not success:
                                        response_message = await ctx.respond(
                                            language_helper.response_location_edit_failed
                                        )
                                        await bot.utils.handle_auto_delete(
                                            ctx.channel_id, response_message, auto_delete_helper
                                        )
                                        if guild_log_settings.log_errors:
                                            log_response = language_helper.log_response_location_edit_failed.format(
                                                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                                member=ctx.member,
                                                location_type=location_type,
                                            )
                                            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                                        return

                                new_location = LocationsUpdate(
                                    guild_id=ctx.guild_id, longitude=longitude, latitude=latitude
                                )

                                try:
                                    _ = await bot.database.change_location(location_exists, new_location)
                                except DatabaseError:
                                    response_message = await ctx.respond(language_helper.response_location_edit_failed)
                                    await bot.utils.handle_auto_delete(
                                        ctx.channel_id, response_message, auto_delete_helper
                                    )
                                    if guild_log_settings.log_errors:
                                        log_response = language_helper.log_response_location_edit_failed.format(
                                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                            member=ctx.member,
                                            location_type=location_type,
                                        )
                                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                                    raise

                                response_message = await ctx.respond(language_helper.response_location_edit_success)
                                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                                if guild_log_settings.log_location_add:
                                    log_response = language_helper.log_response_location_edit_success.format(
                                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                        member=ctx.member,
                                        location_type=location_type,
                                    )
                                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                            listening = False
                        except TimeoutError:
                            await ctx.delete_response(response_message_edit)
                            listening = False
                        except Exception:
                            logging.getLogger(__name__).exception(
                                "An error occurred while listening for the info command!"
                            )
                            await ctx.delete_response(response_message_edit)
                            listening = False

                listening = False
            except TimeoutError:
                await ctx.delete_response(response_message)
                listening = False
            except Exception:
                logging.getLogger(__name__).exception("An error occurred while listening for the info command!")
                await ctx.delete_response(response_message)
                listening = False

    async def _add_pagination_to_components(
        self, components: list[tuple[hikari.impl.ContainerComponentBuilder]]
    ) -> list[tuple[hikari.impl.ContainerComponentBuilder]]:
        custom_id = "locations,list"
        for component in components:
            component[0].add_separator(divider=True, spacing=hikari.SpacingType.SMALL)
            component[0].add_action_row(
                components=[
                    hikari.impl.InteractiveButtonBuilder(
                        style=hikari.ButtonStyle.PRIMARY, label="<<", custom_id=f"{custom_id},<<"
                    ),
                    hikari.impl.InteractiveButtonBuilder(
                        style=hikari.ButtonStyle.PRIMARY, label="<", custom_id=f"{custom_id},<"
                    ),
                    hikari.impl.InteractiveButtonBuilder(
                        style=hikari.ButtonStyle.PRIMARY, label=">", custom_id=f"{custom_id},>"
                    ),
                    hikari.impl.InteractiveButtonBuilder(
                        style=hikari.ButtonStyle.PRIMARY, label=">>", custom_id=f"{custom_id},>>"
                    ),
                ]
            )
        return components

    async def _handle_listening(
        self,
        components: list[tuple[hikari.impl.ContainerComponentBuilder]],
        ctx: lightbulb.Context,
        bot: Bot,
        auto_delete_helper: int,
        response_id: hikari.Snowflakeish | int | None = None,
    ) -> None:
        index = 0
        if response_id is None:
            response_id = await ctx.respond(components=components[index])
        else:
            await ctx.edit_response(response_id, components=components[index])

        listening = True
        while listening:
            try:
                event = await bot.wait_for(
                    hikari.ComponentInteractionCreateEvent,
                    timeout=max(auto_delete_helper, 30),
                    predicate=lambda event: event.interaction.user.id == ctx.user.id,
                )

                command, action, page = event.interaction.custom_id.split(",")
                if command != "locations" or action != "list":
                    return

                await event.interaction.create_initial_response(6)

                if page == "<<":
                    index = 0
                elif page == "<":
                    index = (index - 1) % len(components)
                elif page == ">":
                    index = (index + 1) % len(components)
                elif page == ">>":
                    index = len(components) - 1

                await ctx.interaction.edit_initial_response(components=components[index])
            except TimeoutError:
                await ctx.delete_response(response_id)
                listening = False
            except Exception:
                logging.getLogger(__name__).exception("An error occurred while listening for the tags list command!")
                await ctx.delete_response(response_id)
                listening = False

    async def _get_location_name(
        self, ctx: lightbulb.Context, event: hikari.ComponentInteractionCreateEvent, bot: Bot, location_type: str
    ) -> tuple[bool, str]:
        if ctx.guild_id is None:
            await ctx.respond("Command must be executed in a server.")
            return False, ""

        guild_settings = await bot.database.get_guild_settings(ctx.guild_id)
        if guild_settings is None:
            await ctx.respond("Command must be executed in a server.")
            return False, ""

        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
        auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)
        auto_delete_helper = max(auto_delete_helper, 120)

        location_name_modal = LocationNameModal(guild_settings.language, location_type)
        await event.interaction.create_modal_response(
            language_helper.location_name_modal_location_name, "_get_location_name", components=location_name_modal
        )

        try:
            await location_name_modal.attach(bot.client, "_get_location_name", timeout=auto_delete_helper)
        except TimeoutError:
            return False, ""
        else:
            if location_name_modal.selected_btn == "_get_location_name" and (
                location_name_modal.given_location_name is not None
            ):
                return True, location_name_modal.given_location_name.lower()

        return False, ""

    async def _get_location_description(
        self, ctx: lightbulb.Context, event: hikari.ComponentInteractionCreateEvent, bot: Bot, location_type: str
    ) -> tuple[bool, str | None]:
        if ctx.guild_id is None:
            await ctx.respond("Command must be executed in a server.")
            return False, ""

        guild_settings = await bot.database.get_guild_settings(ctx.guild_id)
        if guild_settings is None:
            await ctx.respond("Command must be executed in a server.")
            return False, ""

        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
        auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)
        auto_delete_helper = max(auto_delete_helper, 120)

        location_description_modal = LocationDescriptionModal(guild_settings.language, location_type)
        await event.interaction.create_modal_response(
            language_helper.location_description_modal_location_name,
            "_get_location_description",
            components=location_description_modal,
        )

        try:
            await location_description_modal.attach(bot.client, "_get_location_description", timeout=auto_delete_helper)
        except TimeoutError:
            return False, ""
        else:
            if location_description_modal.selected_btn == "_get_location_description" and (
                location_description_modal.given_location_description is not None
            ):
                if location_description_modal.given_location_description.lower().strip().replace(" ", "") == "":
                    return True, None
                return True, location_description_modal.given_location_description.lower().strip().replace(
                    " ", ""
                ).lower()

        return False, ""

    async def _get_location_long_lat(
        self, ctx: lightbulb.Context, event: hikari.ComponentInteractionCreateEvent, bot: Bot, location_type: str
    ) -> tuple[bool, float | None, float | None]:
        if ctx.guild_id is None:
            await ctx.respond("Command must be executed in a server.")
            return False, 0, 0

        guild_settings = await bot.database.get_guild_settings(ctx.guild_id)
        if guild_settings is None:
            await ctx.respond("Command must be executed in a server.")
            return False, 0, 0

        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
        auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)
        auto_delete_helper = max(auto_delete_helper, 120)

        location_long_lat_modal = LocationLongLatModal(guild_settings.language, location_type)
        await event.interaction.create_modal_response(
            language_helper.location_longitude_latitude_modal_location_name,
            "_get_location_long_lat",
            components=location_long_lat_modal,
        )

        try:
            await location_long_lat_modal.attach(bot.client, "_get_location_long_lat", timeout=auto_delete_helper)
        except TimeoutError:
            return False, 0, 0
        else:
            if (
                location_long_lat_modal.selected_btn == "_get_location_long_lat"
                and location_long_lat_modal.given_location_long is not None
                and location_long_lat_modal.given_location_lat is not None
            ):
                valid_latitude, valid_longitude = await bot.utils.validate_latitude_longitude_type(
                    location_long_lat_modal.given_location_lat, location_long_lat_modal.given_location_long
                )
                if not valid_latitude or not valid_longitude:
                    return False, None, None

                return (
                    True,
                    float(location_long_lat_modal.given_location_long),
                    float(location_long_lat_modal.given_location_lat),
                )

        return False, 0, 0
