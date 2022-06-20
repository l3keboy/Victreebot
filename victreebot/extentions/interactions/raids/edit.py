# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
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
from utils.helpers.contants import SUPPORTED_RAID_TYPES
from utils.helpers.contants import SUPPORTED_LOCATION_TYPES
from extentions.interactions.raids.create import get_boss_name
from extentions.interactions.raids.create import get_location_name

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.with_str_slash_option("raid_id", "The ID of the raid to edit")
@tanjun.as_slash_command("edit", "Edit an existing raid.")
async def command_raid_edit(
    ctx: tanjun.abc.SlashContext,
    raid_id: str,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, is_setup, moderator_role_id, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup", "moderator_role_id"]
    )
    log_errors, log_raid_edit, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_raid_edit"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    raid = bot_aware.raids.get(f"'{raid_id}'")
    if raid is None:
        response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_no_raid_found
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_no_raid_found.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return

    if ctx.author.id != raid.raid_creator_id and ctx.author.id != moderator_role_id:
        response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_not_creator_or_moderator.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_not_creator_or_moderator.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, bot_name=BOT_NAME.capitalize()
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return

    timeout = 120
    raid_edit_action_row = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.PRIMARY, "edit_raid_type")
        .set_label(SUPPORTED_LANGUAGES.get(language).raid_edit_action_row_edit_raid_type)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "edit_boss")
        .set_label(SUPPORTED_LANGUAGES.get(language).raid_edit_action_row_edit_boss)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "edit_location")
        .set_label(SUPPORTED_LANGUAGES.get(language).raid_edit_action_row_edit_location)
        .add_to_container()
    )

    raid_edit_embed = (
        hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).raid_edit_embed_title,
            description=SUPPORTED_LANGUAGES.get(language).raid_edit_embed_description,
            colour=hikari.Colour(0x8bc683),
        )
    )

    response_message = await ctx.respond(embed=raid_edit_embed, components=[raid_edit_action_row])

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ComponentInteraction)
            and event.interaction.user.id == ctx.author.id
            and event.interaction.message.id == response_message.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_timeout_reached
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        raid = bot_aware.raids.get(f"'{raid_id}'")
        if event.interaction.custom_id == "edit_raid_type":
            await event.interaction.create_initial_response(6)
            # GET RAID TYPE
            raid_type_action_row = (
                ctx.rest.build_action_row()
            )
            for raid_type in SUPPORTED_RAID_TYPES:
                raid_type_action_row.add_button(hikari.ButtonStyle.PRIMARY, raid_type.lower()).set_label(raid_type).add_to_container()

            raid_type_embed = (
                hikari.Embed(
                    title=SUPPORTED_LANGUAGES.get(language).raid_create_embed_title_raid_type,
                    description=SUPPORTED_LANGUAGES.get(language).raid_create_embed_description_raid_type,
                    colour=hikari.Colour(0x8bc683),
                )
            )

            response_message = await ctx.edit_last_response(embed=raid_type_embed, components=[raid_type_action_row])

            try:
                event = await ctx.client.events.wait_for(
                    hikari.InteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: isinstance(event.interaction, hikari.ComponentInteraction)
                    and event.interaction.user.id == ctx.author.id
                    and event.interaction.message.id == response_message.id,
                )
            except asyncio.TimeoutError:
                response = SUPPORTED_LANGUAGES.get(language).response_raid_create_timeout_reached
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_create_timeout_reached.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return
            else:
                raid_type = event.interaction.custom_id
                success = await raid.update_raid(new_type=raid_type)
                if not success:
                    response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_raid_type_failed
                    await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                    if log_errors:
                        log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_failed.format(
                            datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                        )
                        await bot.log_from_ctx(ctx, db, log_response)
                    return

                response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_raid_type
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_raid_edit:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "edit_boss":
            boss_name = await get_boss_name(ctx, event, db, bot, bot_aware)
            success, pokemon, pokemon_image = await bot.validate_pokemon(boss_name)
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_raid_create_unknown_boss.format(boss_name=boss_name)
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_create_unknown_boss.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            success = await raid.update_raid(new_boss=pokemon.name.lower())
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_boss_failed
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_failed.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_raid_type
            await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
            if log_raid_edit:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                )
                await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "edit_location":
            await event.interaction.create_initial_response(6)
            # GET LOCATION TYPE
            location_type_action_row = (
                ctx.rest.build_action_row()
            )
            for location_type in SUPPORTED_LOCATION_TYPES:
                location_type_action_row.add_button(hikari.ButtonStyle.PRIMARY, location_type.lower()).set_label(location_type).add_to_container()

            location_type_embed = (
                hikari.Embed(
                    title=SUPPORTED_LANGUAGES.get(language).raid_create_embed_title_location_type,
                    description=SUPPORTED_LANGUAGES.get(language).raid_create_embed_description_location_type,
                    colour=hikari.Colour(0x8bc683),
                )
            )

            response_message = await ctx.edit_last_response(embed=location_type_embed, components=[location_type_action_row])

            try:
                event = await ctx.client.events.wait_for(
                    hikari.InteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: isinstance(event.interaction, hikari.ComponentInteraction)
                    and event.interaction.user.id == ctx.author.id
                    and event.interaction.message.id == response_message.id,
                )
            except asyncio.TimeoutError:
                response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_timeout_reached
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_timeout_reached.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return
            else:
                location_type = event.interaction.custom_id
                location_type = f"'{location_type}'"

            # GET LOCATION NAME
            location_name_awnser = await get_location_name(ctx, event, location_type, db, bot, bot_aware)
            location_name = location_name_awnser.replace("'", "''")
            location_name = f"'{location_name}'"

            all_locations = []
            results = await db.get_all_locations(ctx.get_guild(), location_type)
            for location in results:
                all_locations.append(location.get("name"))

            if location_name_awnser.lower() not in all_locations:
                response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_location_not_found.format(location_type=location_type.strip("'"), location_name=location_name_awnser)
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_location_not_found.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            success = await raid.update_raid(new_location=location_name, new_location_type=location_type)
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_location_failed
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_failed.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            response = SUPPORTED_LANGUAGES.get(language).response_raid_location_raid_type
            await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
            if log_raid_edit:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                )
                await bot.log_from_ctx(ctx, db, log_response)