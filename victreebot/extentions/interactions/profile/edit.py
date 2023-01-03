# IMPORTS
import asyncio
import os

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
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.as_slash_command("edit", "Edit your profile")
async def command_profile_edit(
    ctx: tanjun.abc.SlashContext,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup"]
    )
    log_errors, log_profile_edit, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_profile_edit"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    timeout = 120
    embed = hikari.Embed(
        title=SUPPORTED_LANGUAGES.get(language).profile_edit_embed_title,
        description=SUPPORTED_LANGUAGES.get(language).profile_edit_embed_description,
        colour=hikari.Colour(0x8BC683),
    )

    action_row_1 = (
        ctx.rest.build_message_action_row()
        .add_button(hikari.ButtonStyle.SUCCESS, "add_friend_codes")
        .set_label(SUPPORTED_LANGUAGES.get(language).profile_action_row_add_friend_code)
        .add_to_container()
        .add_button(hikari.ButtonStyle.DANGER, "delete_friend_codes")
        .set_label(SUPPORTED_LANGUAGES.get(language).profile_action_row_delete_friend_code)
        .add_to_container()
    )
    action_row_2 = (
        ctx.rest.build_message_action_row()
        .add_button(hikari.ButtonStyle.SUCCESS, "add_active_locations")
        .set_label(SUPPORTED_LANGUAGES.get(language).profile_action_row_add_active_location)
        .add_to_container()
        .add_button(hikari.ButtonStyle.DANGER, "delete_active_locations")
        .set_label(SUPPORTED_LANGUAGES.get(language).profile_action_row_delete_active_location)
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
        response = SUPPORTED_LANGUAGES.get(language).response_profile_edit_timeout_reached
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_edit_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        if event.interaction.custom_id == "add_friend_codes":
            add_friend_code_action_row = (
                ctx.rest.build_modal_action_row()
                .add_text_input(
                    label=SUPPORTED_LANGUAGES.get(language).profile_modal_add_friend_codes_text_input_title,
                    custom_id="friend_codes",
                )
                .set_placeholder(
                    SUPPORTED_LANGUAGES.get(language).profile_modal_add_friend_codes_text_input_placeholder
                )
                .add_to_container()
            )
            await event.interaction.create_modal_response(
                SUPPORTED_LANGUAGES.get(language).profile_modal_add_friend_codes,
                "friend_codes_modal",
                components=[add_friend_code_action_row],
            )

            try:
                event = await ctx.client.events.wait_for(
                    hikari.InteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
                    and event.interaction.user.id == ctx.author.id,
                )
            except asyncio.TimeoutError:
                response = SUPPORTED_LANGUAGES.get(language).response_profile_edit_timeout_reached
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_edit_timeout_reached.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return
            else:
                await event.interaction.create_initial_response(6)
                if event.interaction.custom_id == "friend_codes_modal":
                    if event.interaction.components[0][0].value is not None:
                        current_friend_codes, *none = await db.get_user_details(
                            ctx.get_guild(), ctx.member, details=["friend_codes"]
                        )
                        if current_friend_codes is not None:
                            current_friend_codes = current_friend_codes.strip("'")
                            current_friend_codes_list = current_friend_codes.split(",")

                        if (
                            current_friend_codes is None
                            or current_friend_codes_list is None
                            or current_friend_codes_list == []
                        ):
                            current_friend_codes_list = []

                        friend_codes_list = event.interaction.components[0][0].value.split(",")
                        for friend_code in friend_codes_list:
                            friend_code = friend_code.replace("-", " ")
                            friend_code = friend_code.lstrip()
                            friend_code = friend_code.rstrip()
                            correct_friend_code_format = await bot.validate_friend_code(friend_code)
                            if not correct_friend_code_format:
                                response = SUPPORTED_LANGUAGES.get(
                                    language
                                ).response_profile_edit_invalid_friend_code_format
                                await ctx.edit_last_response(
                                    response, delete_after=auto_delete, embed=None, components=None
                                )
                                if log_errors:
                                    log_response = SUPPORTED_LANGUAGES.get(
                                        language
                                    ).log_response_profile_edit_invalid_friend_code_format.format(
                                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                                    )
                                    await bot.log_from_ctx(ctx, db, log_response)
                                return
                            if friend_code not in current_friend_codes_list:
                                current_friend_codes_list.append(friend_code)

                        friend_codes_to_add = f'{",".join(friend_code for friend_code in current_friend_codes_list)}'
                        friend_codes_to_add = f"'{friend_codes_to_add}'"
                        parameters = []
                        parameters.append(f"friend_codes = {friend_codes_to_add}")
                        await db.set_user_detail(ctx.get_guild(), ctx.member, parameters=parameters)

                        response = SUPPORTED_LANGUAGES.get(language).response_profile_edit_success
                        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                        if log_profile_edit:
                            log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_edit.format(
                                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                            )
                            await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "delete_friend_codes":
            delete_friend_code_action_row = (
                ctx.rest.build_modal_action_row()
                .add_text_input(
                    label=SUPPORTED_LANGUAGES.get(language).profile_modal_delete_friend_codes_text_input_title,
                    custom_id="friend_codes",
                )
                .set_placeholder(
                    SUPPORTED_LANGUAGES.get(language).profile_modal_delete_friend_codes_text_input_placeholder
                )
                .add_to_container()
            )
            await event.interaction.create_modal_response(
                SUPPORTED_LANGUAGES.get(language).profile_modal_delete_friend_codes,
                "friend_codes_modal",
                components=[delete_friend_code_action_row],
            )

            try:
                event = await ctx.client.events.wait_for(
                    hikari.InteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
                    and event.interaction.user.id == ctx.author.id,
                )
            except asyncio.TimeoutError:
                response = SUPPORTED_LANGUAGES.get(language).response_profile_edit_timeout_reached
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_edit_timeout_reached.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return
            else:
                await event.interaction.create_initial_response(6)
                if event.interaction.custom_id == "friend_codes_modal":
                    if event.interaction.components[0][0].value is not None:
                        current_friend_codes, *none = await db.get_user_details(
                            ctx.get_guild(), ctx.member, details=["friend_codes"]
                        )
                        if current_friend_codes is not None:
                            current_friend_codes = current_friend_codes.strip("'")
                            current_friend_codes_list = current_friend_codes.split(",")

                        if (
                            current_friend_codes is None
                            or current_friend_codes_list is None
                            or current_friend_codes_list == []
                        ):
                            current_friend_codes_list = []

                        friend_codes_list = event.interaction.components[0][0].value.split(",")
                        for friend_code in friend_codes_list:
                            friend_code = friend_code.replace("-", " ")
                            friend_code = friend_code.lstrip()
                            friend_code = friend_code.rstrip()
                            correct_friend_code_format = await bot.validate_friend_code(friend_code)
                            if not correct_friend_code_format:
                                response = SUPPORTED_LANGUAGES.get(
                                    language
                                ).response_profile_edit_invalid_friend_code_format
                                await ctx.edit_last_response(
                                    response, delete_after=auto_delete, embed=None, components=None
                                )
                                if log_errors:
                                    log_response = SUPPORTED_LANGUAGES.get(
                                        language
                                    ).log_response_profile_edit_invalid_friend_code_format.format(
                                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                                    )
                                    await bot.log_from_ctx(ctx, db, log_response)
                                return
                            if friend_code in current_friend_codes_list:
                                current_friend_codes_list.remove(friend_code)

                        if current_friend_codes_list != []:
                            friend_codes_to_delete = (
                                f'{",".join(friend_code for friend_code in current_friend_codes_list)}'
                            )
                            friend_codes_to_delete = f"'{friend_codes_to_delete}'"
                        else:
                            friend_codes_to_delete = "NULL"
                        parameters = []
                        parameters.append(f"friend_codes = {friend_codes_to_delete}")
                        await db.set_user_detail(ctx.get_guild(), ctx.member, parameters=parameters)

                        response = SUPPORTED_LANGUAGES.get(language).response_profile_edit_success
                        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                        if log_profile_edit:
                            log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_edit.format(
                                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                            )
                            await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "add_active_locations":
            add_active_locations_action_row = (
                ctx.rest.build_modal_action_row()
                .add_text_input(
                    label=SUPPORTED_LANGUAGES.get(language).profile_modal_add_active_locations_text_input_title,
                    custom_id="active_locations",
                )
                .set_placeholder(
                    SUPPORTED_LANGUAGES.get(language).profile_modal_add_active_locations_text_input_placeholder
                )
                .add_to_container()
            )
            await event.interaction.create_modal_response(
                SUPPORTED_LANGUAGES.get(language).profile_modal_add_active_locations,
                "active_locations_modal",
                components=[add_active_locations_action_row],
            )

            try:
                event = await ctx.client.events.wait_for(
                    hikari.InteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
                    and event.interaction.user.id == ctx.author.id,
                )
            except asyncio.TimeoutError:
                response = SUPPORTED_LANGUAGES.get(language).response_profile_edit_timeout_reached
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_edit_timeout_reached.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return
            else:
                await event.interaction.create_initial_response(6)
                if event.interaction.custom_id == "active_locations_modal":
                    if event.interaction.components[0][0].value is not None:
                        current_active_locations, *none = await db.get_user_details(
                            ctx.get_guild(), ctx.member, details=["active_locations"]
                        )
                        if current_active_locations is not None:
                            current_active_locations = current_active_locations.strip("'")
                            current_active_locations_list = current_active_locations.split(",")

                        if (
                            current_active_locations is None
                            or current_active_locations_list is None
                            or current_active_locations_list == []
                        ):
                            current_active_locations_list = []

                        active_locations_list = event.interaction.components[0][0].value.split(",")
                        for location in active_locations_list:
                            location = location.lstrip()
                            location = location.rstrip()
                            location = location.lower()
                            if location not in current_active_locations_list:
                                current_active_locations_list.append(location)

                        active_locations_to_add = f'{",".join(location for location in current_active_locations_list)}'
                        active_locations_to_add = f"'{active_locations_to_add}'"
                        parameters = []
                        parameters.append(f"active_locations = {active_locations_to_add}")
                        await db.set_user_detail(ctx.get_guild(), ctx.member, parameters=parameters)

                        response = SUPPORTED_LANGUAGES.get(language).response_profile_edit_success
                        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                        if log_profile_edit:
                            log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_edit.format(
                                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                            )
                            await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "delete_active_locations":
            delete_active_locations_action_row = (
                ctx.rest.build_modal_action_row()
                .add_text_input(
                    label=SUPPORTED_LANGUAGES.get(language).profile_modal_delete_active_locations_text_input_title,
                    custom_id="active_locations",
                )
                .set_placeholder(
                    SUPPORTED_LANGUAGES.get(language).profile_modal_delete_active_locations_text_input_placeholder
                )
                .add_to_container()
            )
            await event.interaction.create_modal_response(
                SUPPORTED_LANGUAGES.get(language).profile_modal_delete_active_locations,
                "active_locations_modal",
                components=[delete_active_locations_action_row],
            )

            try:
                event = await ctx.client.events.wait_for(
                    hikari.InteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
                    and event.interaction.user.id == ctx.author.id,
                )
            except asyncio.TimeoutError:
                response = SUPPORTED_LANGUAGES.get(language).response_profile_edit_timeout_reached
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_edit_timeout_reached.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return
            else:
                await event.interaction.create_initial_response(6)
                if event.interaction.custom_id == "active_locations_modal":
                    if event.interaction.components[0][0].value is not None:
                        current_active_locations, *none = await db.get_user_details(
                            ctx.get_guild(), ctx.member, details=["active_locations"]
                        )
                        if current_active_locations is not None:
                            current_active_locations = current_active_locations.strip("'")
                            current_active_locations_list = current_active_locations.split(",")

                        if (
                            current_active_locations is None
                            or current_active_locations_list is None
                            or current_active_locations_list == []
                        ):
                            current_active_locations_list = []

                        active_locations_list = event.interaction.components[0][0].value.split(",")
                        for location in active_locations_list:
                            location = location.lstrip()
                            location = location.rstrip()
                            location = location.lower()
                            if location in current_active_locations_list:
                                current_active_locations_list.remove(location)

                        if current_active_locations_list != []:
                            active_locations_to_delete = (
                                f'{",".join(location for location in current_active_locations_list)}'
                            )
                            active_locations_to_delete = f"'{active_locations_to_delete}'"
                        else:
                            active_locations_to_delete = "NULL"

                        parameters = []
                        parameters.append(f"active_locations = {active_locations_to_delete}")
                        await db.set_user_detail(ctx.get_guild(), ctx.member, parameters=parameters)

                        response = SUPPORTED_LANGUAGES.get(language).response_profile_edit_success
                        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                        if log_profile_edit:
                            log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_edit.format(
                                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                            )
                            await bot.log_from_ctx(ctx, db, log_response)
