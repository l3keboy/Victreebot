# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import asyncio
import math
import os
from typing import Tuple

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# FUNCTIONS #
# ------------------------------------------------------------------------- #
async def get_location_name(
    ctx: tanjun.abc.SlashContext,
    event: hikari.InteractionCreateEvent,
    location_type: str,
    db: DatabaseHandler,
    bot: BotUtils,
    bot_aware: Bot,
) -> str:
    language, auto_delete, gmt, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt"]
    )
    log_errors, *none = await db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors"])

    timeout = 120
    location_name_action_row = (
        ctx.rest.build_action_row()
        .add_text_input(
            label=SUPPORTED_LANGUAGES.get(language).location_name_modal_text_input_title.format(
                location=location_type.strip("'")
            ),
            custom_id="location_name",
        )
        .set_placeholder(SUPPORTED_LANGUAGES.get(language).location_name_modal_text_input_placeholder)
        .set_required(True)
        .add_to_container()
    )

    await event.interaction.create_modal_response(
        SUPPORTED_LANGUAGES.get(language).location_name_modal_location_name.format(
            location=location_type.strip("'").capitalize()
        ),
        "location_name_modal",
        components=[location_name_action_row],
    )

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
            and event.interaction.user.id == ctx.author.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_location_interactions_timeout_reached
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_interactions_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        await event.interaction.create_initial_response(6)
        if event.interaction.custom_id == "location_name_modal":
            if event.interaction.components[0][0].value is not None:
                location_name = event.interaction.components[0][0].value
                return location_name.lower()


async def get_location_description(
    ctx: tanjun.abc.SlashContext,
    event: hikari.InteractionCreateEvent,
    location_type: str,
    db: DatabaseHandler,
    bot: BotUtils,
    bot_aware: Bot,
) -> str:
    language, auto_delete, gmt, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt"]
    )
    log_errors, *none = await db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors"])

    timeout = 120
    location_description_action_row = (
        ctx.rest.build_action_row()
        .add_text_input(
            label=SUPPORTED_LANGUAGES.get(language).location_description_modal_text_input_title.format(
                location=location_type.strip("'")
            ),
            custom_id="location_description",
        )
        .set_placeholder(SUPPORTED_LANGUAGES.get(language).location_description_modal_text_input_placeholder)
        .set_required(True)
        .add_to_container()
    )

    await event.interaction.create_modal_response(
        SUPPORTED_LANGUAGES.get(language).location_description_modal_location_name.format(
            location=location_type.strip("'").capitalize()
        ),
        "location_description_modal",
        components=[location_description_action_row],
    )

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
            and event.interaction.user.id == ctx.author.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_location_interactions_timeout_reached
        await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_interactions_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        await event.interaction.create_initial_response(6)
        if event.interaction.custom_id == "location_description_modal":
            location_description = event.interaction.components[0][0].value
            if location_description == "":
                location_description = None
                return location_description
            else:
                return location_description.lower()


async def get_location_latitude_longitude(
    ctx: tanjun.abc.SlashContext,
    event: hikari.InteractionCreateEvent,
    location_type: str,
    db: DatabaseHandler,
    bot: BotUtils,
    bot_aware: Bot,
) -> Tuple[str, str]:
    language, auto_delete, gmt, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt"]
    )
    log_errors, *none = await db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors"])

    timeout = 120
    location_longitude_action_row = (
        ctx.rest.build_action_row()
        .add_text_input(
            label=SUPPORTED_LANGUAGES.get(language).location_longitude_modal_text_input_title.format(
                location=location_type.strip("'")
            ),
            custom_id="location_longitude",
        )
        .set_placeholder(SUPPORTED_LANGUAGES.get(language).location_longitude_modal_text_input_placeholder)
        .set_required(True)
        .add_to_container()
    )
    location_latitude_action_row = (
        ctx.rest.build_action_row()
        .add_text_input(
            label=SUPPORTED_LANGUAGES.get(language).location_latitude_modal_text_input_title.format(
                location=location_type.strip("'")
            ),
            custom_id="location_latitude",
        )
        .set_placeholder(SUPPORTED_LANGUAGES.get(language).location_latitude_modal_text_input_placeholder)
        .set_required(True)
        .add_to_container()
    )

    await event.interaction.create_modal_response(
        SUPPORTED_LANGUAGES.get(language).location_longitude_latitude_modal_location_name.format(
            location=location_type.strip("'").capitalize()
        ),
        "location_longitude_latitude_modal",
        components=[location_latitude_action_row, location_longitude_action_row],
    )

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
            and event.interaction.user.id == ctx.author.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_location_interactions_timeout_reached
        await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_interactions_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        await event.interaction.create_initial_response(6)
        if event.interaction.custom_id == "location_longitude_latitude_modal":
            if (
                event.interaction.components[0][0].value is not None
                and event.interaction.components[1][0].value is not None
            ):
                latitude = event.interaction.components[0][0].value
                longitude = event.interaction.components[1][0].value
                valid_latitude, valid_longitude = await bot.validate_latitude_longitude_type(latitude, longitude)
                if not valid_latitude or not valid_longitude:
                    return None, None

                valid_latitude, valid_longitude = await bot.validate_latitude_longitude_range(latitude, longitude)
                if not valid_latitude or not valid_longitude:
                    return None, None

                return latitude, longitude


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.as_slash_command("locations", "Interacions for locations")
async def command_locations(
    ctx: tanjun.abc.SlashContext,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup"]
    )
    (
        log_errors,
        log_location_add,
        log_location_delete,
        log_location_edit,
        log_location_info,
        log_location_list,
        *none,
    ) = await db.get_guild_log_settings(
        ctx.get_guild(),
        settings=[
            "log_errors",
            "log_location_add",
            "log_location_delete",
            "log_location_edit",
            "log_location_info",
            "log_location_list",
        ],
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    timeout = 120
    embed = hikari.Embed(
        title=SUPPORTED_LANGUAGES.get(language).location_embed_title,
        description=SUPPORTED_LANGUAGES.get(language).location_embed_description,
        colour=hikari.Colour(0x8BC683),
    )

    action_row_1 = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.SUCCESS, "add_gym")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_add_gym)
        .add_to_container()
        .add_button(hikari.ButtonStyle.DANGER, "delete_gym")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_delete_gym)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "edit_gym")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_edit_gym)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "list_gyms")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_list_gym)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "info_gym")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_info_gym)
        .add_to_container()
    )
    action_row_2 = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.SUCCESS, "add_pokestop")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_add_pokestop)
        .add_to_container()
        .add_button(hikari.ButtonStyle.DANGER, "delete_pokestop")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_delete_pokestop)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "edit_pokestop")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_edit_pokestop)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "list_pokestops")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_list_pokestop)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "info_pokestop")
        .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_info_pokestop)
        .add_to_container()
    )

    response_message = await ctx.respond(embed, components=[action_row_1, action_row_2])

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ComponentInteraction)
            and event.interaction.user.id == ctx.author.id
            and event.interaction.message.id == response_message.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_location_interactions_timeout_reached
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_interactions_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        await response_message.delete()
        if event.interaction.custom_id == "list_gyms" or event.interaction.custom_id == "list_pokestops":
            location_type = "gym" if event.interaction.custom_id == "list_gyms" else "pokéstop"
            location_type = f"'{location_type}'"

            all_locations = []
            results = await db.get_all_locations(ctx.get_guild(), location_type)
            for location in results:
                all_locations.append(location.get("name"))

            if all_locations == []:
                response = SUPPORTED_LANGUAGES.get(language).response_location_list_no_results.format(
                    location_type=location_type.strip("'")
                )
                await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_list_no_results.format(
                        datetime=await bot.get_timestamp_aware(gmt),
                        member=ctx.member,
                        location_type=location_type.strip("'"),
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            if log_location_list:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_list_requested.format(
                    datetime=await bot.get_timestamp_aware(gmt),
                    member=ctx.member,
                    location_type=location_type.strip("'"),
                )
                await bot.log_from_ctx(ctx, db, log_response)

            if len(all_locations) < 11:
                auto_delete = 20 if auto_delete < 20 else auto_delete

                known_coordinates = (
                    "[{google_maps_translation}](https://www.google.com/maps/place/{latitude},{longitude})"
                )
                unknown_coordinates = f"`{SUPPORTED_LANGUAGES.get(language).location_no_coordinates_set}`"

                embed = hikari.Embed(
                    title=SUPPORTED_LANGUAGES.get(language).location_list_embed_title,
                    description=SUPPORTED_LANGUAGES.get(language).location_list_embed_description.format(
                        location_type=location_type.strip("'")
                    ),
                    colour=hikari.Colour(0x8BC683),
                ).add_field(
                    name=SUPPORTED_LANGUAGES.get(language).location_list_embed_field_locations,
                    value="\n".join(
                        f"***{location.get('name')}***"
                        + " \n"
                        + f"{known_coordinates.format(google_maps_translation=SUPPORTED_LANGUAGES.get(language).location_google_maps, latitude=location.get('latitude'), longitude=location.get('longitude')) if location.get('latitude') is not None and location.get('longitude') is not None else unknown_coordinates}"  # noqa E501
                        + "\n"
                        for location in results
                    ),
                    inline=False,
                )

                await ctx.create_followup(embed=embed, delete_after=auto_delete, components=None)
            else:
                auto_delete = 45 if auto_delete < 45 else auto_delete

                i, start, end, max_length = 1, 0, 10, 10
                values = []
                pages = math.ceil(len(results) / max_length)

                known_coordinates = (
                    "[{google_maps_translation}](https://www.google.com/maps/place/{latitude},{longitude})"
                )
                unknown_coordinates = f"`{SUPPORTED_LANGUAGES.get(language).location_no_coordinates_set}`"

                while i <= pages:
                    embed = hikari.Embed(
                        title=SUPPORTED_LANGUAGES.get(language).location_list_embed_title,
                        description=SUPPORTED_LANGUAGES.get(language).location_list_embed_description.format(
                            location_type=location_type.strip("'")
                        ),
                        colour=hikari.Colour(0x8BC683),
                    ).add_field(
                        name=SUPPORTED_LANGUAGES.get(language).location_list_embed_field_locations,
                        value="\n".join(
                            f"***{location.get('name')}***"
                            + " \n"
                            + f"{known_coordinates.format(google_maps_translation=SUPPORTED_LANGUAGES.get(language).location_google_maps, latitude=location.get('latitude'), longitude=location.get('longitude')) if location.get('latitude') is not None and location.get('longitude') is not None else unknown_coordinates}"  # noqa E501
                            + "\n"
                            for location in results
                        ),
                        inline=False,
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

                await ctx.create_followup(values[0], component=button_menu)

                while True:
                    try:
                        event = await ctx.client.events.wait_for(
                            hikari.InteractionCreateEvent,
                            timeout=auto_delete,
                            predicate=lambda event: isinstance(event.interaction, hikari.ComponentInteraction)
                            and event.interaction.user.id == ctx.author.id
                            and event.interaction.message.id == response_message.id,
                        )
                    except asyncio.TimeoutError:
                        response = SUPPORTED_LANGUAGES.get(language).response_location_interactions_timeout_reached
                        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                        if log_errors:
                            log_response = SUPPORTED_LANGUAGES.get(
                                language
                            ).log_response_location_interactions_timeout_reached.format(
                                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                            )
                            await bot.log_from_ctx(ctx, db, log_response)
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
                            hikari.interactions.base_interactions.ResponseType.DEFERRED_MESSAGE_UPDATE, values[index]
                        )

        elif event.interaction.custom_id == "info_gym" or event.interaction.custom_id == "info_pokestop":
            location_type = "gym" if event.interaction.custom_id == "info_gym" else "pokéstop"
            location_type = f"'{location_type}'"

            location_name = await get_location_name(ctx, event, location_type, db, bot, bot_aware)
            location_name = location_name.replace("'", "''")
            location_name = f"'{location_name}'"
            results = await db.get_location_info(ctx.get_guild(), location_type, location_name)
            if results == []:
                response = SUPPORTED_LANGUAGES.get(language).response_location_info_no_results.format(
                    location_type=location_type.strip("'")
                )
                await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_info_no_results.format(
                        datetime=await bot.get_timestamp_aware(gmt),
                        member=ctx.member,
                        location_type=location_type.strip("'"),
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            known_coordinates = "[{google_maps_translation}](https://www.google.com/maps/place/{latitude},{longitude})"
            unknown_coordinates = f"`{SUPPORTED_LANGUAGES.get(language).location_no_coordinates_set}`"

            auto_delete = 20 if auto_delete < 20 else auto_delete
            embed = (
                hikari.Embed(
                    title=SUPPORTED_LANGUAGES.get(language).location_info_embed_title,
                    description=f"""`{location_type.capitalize().strip("'")}:` {location_name.capitalize().strip("'")}\n `Description:` {results[0].get('description') if results[0].get('description') else SUPPORTED_LANGUAGES.get(language).location_no_description_set}""",  # noqa E501
                    colour=hikari.Colour(0x8BC683),
                )
                .add_field(
                    name=SUPPORTED_LANGUAGES.get(language).location_info_embed_field_coordinates,
                    value=f"Latitude: {'`'+str(results[0].get('latitude'))+'`' if results[0].get('latitude') else unknown_coordinates}\n Longitude: {'`'+str(results[0].get('longitude'))+'`' if results[0].get('longitude') else unknown_coordinates}",  # noqa E501
                    inline=False,
                )
                .add_field(
                    name=SUPPORTED_LANGUAGES.get(language).location_info_embed_field_google_maps,
                    value=f"{known_coordinates.format(google_maps_translation=SUPPORTED_LANGUAGES.get(language).location_google_maps, latitude=str(results[0].get('latitude')), longitude=str(results[0].get('longitude'))) if results[0].get('latitude') is not None and results[0].get('longitude') is not None else unknown_coordinates}",  # noqa E501
                    inline=False,
                )
            )

            await ctx.create_followup(embed=embed, delete_after=auto_delete, components=None)
            if log_location_info:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_info_requested.format(
                    datetime=await bot.get_timestamp_aware(gmt),
                    member=ctx.member,
                    location_type=location_type.strip("'"),
                )
                await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "add_gym" or event.interaction.custom_id == "add_pokestop":
            location_type = "gym" if event.interaction.custom_id == "add_gym" else "pokéstop"
            location_name_awnser = await get_location_name(ctx, event, location_type, db, bot, bot_aware)
            location_name = location_name_awnser.replace("'", "''")
            location_type = f"'{location_type}'"

            all_locations = []
            results = await db.get_all_locations(ctx.get_guild(), location_type)
            for location in results:
                all_locations.append(location.get("name"))

            if location_name_awnser.lower() in all_locations:
                response = SUPPORTED_LANGUAGES.get(language).response_location_add_failed_already_exists.format(
                    location_type=location_type.strip("'")
                )
                await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_location_add_failed_already_exists.format(
                        datetime=await bot.get_timestamp_aware(gmt),
                        member=ctx.member,
                        location_type=location_type.strip("'"),
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            event, add = await bot.validate_add_or_no_add(ctx, "a description", db)
            if add:
                location_description = await get_location_description(ctx, event, location_type, db, bot, bot_aware)
            else:
                location_description = "NULL"

            event, add = await bot.validate_add_or_no_add(ctx, "the latitude and longitude", db)
            if add:
                latitude, longitude = await get_location_latitude_longitude(
                    ctx, event, location_type, db, bot, bot_aware
                )
                if latitude is None or longitude is None:
                    response = SUPPORTED_LANGUAGES.get(language).response_location_invalid_latitude_longitude
                    await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                    if log_errors:
                        log_response = SUPPORTED_LANGUAGES.get(
                            language
                        ).log_response_location_invalid_latitude_longitude.format(
                            datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, location_type=location_type
                        )
                        await bot.log_from_ctx(ctx, db, log_response)
                    return
            else:
                latitude, longitude = "NULL", "NULL"

            location_name = f"'{location_name.lower()}'"
            if location_description != "NULL":
                location_description = f"'{location_description}'"
            success = await db.insert_location(
                ctx.get_guild(), location_type, location_name, latitude, longitude, location_description
            )
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_location_add_failed
                await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_add_failed.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, location_type=location_type
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            response = SUPPORTED_LANGUAGES.get(language).response_location_add_success
            await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
            if log_location_add:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_add_success.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, location_type=location_type
                )
                await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "delete_gym" or event.interaction.custom_id == "delete_pokestop":
            location_type = "gym" if event.interaction.custom_id == "delete_gym" else "pokéstop"
            location_name_awnser = await get_location_name(ctx, event, location_type, db, bot, bot_aware)
            location_name = location_name_awnser.replace("'", "''")

            location_type = f"'{location_type}'"

            all_locations = []
            results = await db.get_all_locations(ctx.get_guild(), location_type)
            for location in results:
                all_locations.append(location.get("name"))

            if location_name_awnser.lower() not in all_locations:
                response = SUPPORTED_LANGUAGES.get(language).response_location_delete_failed_no_such_location.format(
                    location_type=location_type.strip("'")
                )
                await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_location_delete_failed_no_such_location.format(
                        datetime=await bot.get_timestamp_aware(gmt),
                        member=ctx.member,
                        location_type=location_type.strip("'"),
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            location_name = f"'{location_name.lower()}'"

            success = await db.delete_location(ctx.get_guild(), location_type, location_name)
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_location_delete_failed
                await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_delete_failed.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, location_type=location_type
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            response = SUPPORTED_LANGUAGES.get(language).response_location_delete_success
            await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
            if log_location_delete:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_delete_success.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, location_type=location_type
                )
                await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "edit_gym" or event.interaction.custom_id == "edit_pokestop":
            location_type = "gym" if event.interaction.custom_id == "edit_gym" else "pokéstop"
            location_name_awnser = await get_location_name(ctx, event, location_type, db, bot, bot_aware)
            location_name = location_name_awnser.replace("'", "''")

            location_type = f"'{location_type}'"

            all_locations = []
            results = await db.get_all_locations(ctx.get_guild(), location_type)
            for location in results:
                all_locations.append(location.get("name"))

            if location_name_awnser.lower() not in all_locations:
                response = SUPPORTED_LANGUAGES.get(language).response_location_edit_failed_no_such_location.format(
                    location_type=location_type.strip("'")
                )
                await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_location_edit_failed_no_such_location.format(
                        datetime=await bot.get_timestamp_aware(gmt),
                        member=ctx.member,
                        location_type=location_type.strip("'"),
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            location_edit_action_row = (
                ctx.rest.build_action_row()
                .add_button(hikari.ButtonStyle.PRIMARY, "location_description")
                .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_edit_description)
                .add_to_container()
                .add_button(hikari.ButtonStyle.PRIMARY, "location_latitude_longitude")
                .set_label(SUPPORTED_LANGUAGES.get(language).location_action_row_edit_latitude_longitude)
                .add_to_container()
            )

            response_message = await ctx.create_followup(embed, components=[location_edit_action_row])

            try:
                event = await ctx.client.events.wait_for(
                    hikari.InteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: isinstance(event.interaction, hikari.ComponentInteraction)
                    and event.interaction.user.id == ctx.author.id
                    and event.interaction.message.id == response_message.id,
                )
            except asyncio.TimeoutError:
                response = SUPPORTED_LANGUAGES.get(language).response_location_interactions_timeout_reached
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_location_interactions_timeout_reached.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return
            else:
                await response_message.delete()
                if event.interaction.custom_id == "location_description":
                    event, add = await bot.validate_add_or_no_add(ctx, "a description", db)
                    if add:
                        location_description = await get_location_description(
                            ctx, event, location_type, db, bot, bot_aware
                        )
                    else:
                        location_description = "NULL"

                    if location_description != "NULL":
                        location_description = f"'{location_description}'"

                    location_name = f"'{location_name.lower()}'"
                    parameters = []
                    parameters.append(f"description = {location_description}")
                    success = await db.edit_location(
                        ctx.get_guild(), location_type, location_name, parameters=parameters
                    )
                    if not success:
                        response = SUPPORTED_LANGUAGES.get(language).response_location_edit_failed
                        await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                        if log_errors:
                            log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_edit_failed.format(
                                datetime=await bot.get_timestamp_aware(gmt),
                                member=ctx.member,
                                location_type=location_type,
                            )
                            await bot.log_from_ctx(ctx, db, log_response)
                        return

                    response = SUPPORTED_LANGUAGES.get(language).response_location_edit_success
                    await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                    if log_location_delete:
                        log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_edit_success.format(
                            datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, location_type=location_type
                        )
                        await bot.log_from_ctx(ctx, db, log_response)

                elif event.interaction.custom_id == "location_latitude_longitude":
                    event, add = await bot.validate_add_or_no_add(ctx, "the latitude and longitude", db)
                    if add:
                        latitude, longitude = await get_location_latitude_longitude(
                            ctx, event, location_type, db, bot, bot_aware
                        )
                        if latitude is None or longitude is None:
                            response = SUPPORTED_LANGUAGES.get(language).response_location_invalid_latitude_longitude
                            await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                            if log_errors:
                                log_response = SUPPORTED_LANGUAGES.get(
                                    language
                                ).log_response_location_invalid_latitude_longitude.format(
                                    datetime=await bot.get_timestamp_aware(gmt),
                                    member=ctx.member,
                                    location_type=location_type,
                                )
                                await bot.log_from_ctx(ctx, db, log_response)
                            return
                    else:
                        latitude, longitude = "NULL", "NULL"

                    location_name = f"'{location_name.lower()}'"
                    parameters = []
                    parameters.append(f"latitude = {latitude}")
                    parameters.append(f"longitude = {longitude}")
                    success = await db.edit_location(
                        ctx.get_guild(), location_type, location_name, parameters=parameters
                    )
                    if not success:
                        response = SUPPORTED_LANGUAGES.get(language).response_location_edit_failed
                        await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                        if log_errors:
                            log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_edit_failed.format(
                                datetime=await bot.get_timestamp_aware(gmt),
                                member=ctx.member,
                                location_type=location_type,
                            )
                            await bot.log_from_ctx(ctx, db, log_response)
                        return

                    response = SUPPORTED_LANGUAGES.get(language).response_location_edit_success
                    await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
                    if log_location_edit:
                        log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_edit_success.format(
                            datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, location_type=location_type
                        )
                        await bot.log_from_ctx(ctx, db, log_response)
