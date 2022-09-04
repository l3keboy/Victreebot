# IMPORTS
import asyncio
import os

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.autocomplete_callbacks import autocomplete_location
from utils.helpers.autocomplete_callbacks import autocomplete_pokemon
from utils.helpers.autocomplete_callbacks import autocomplete_raid_id
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES
from utils.helpers.contants import SUPPORTED_LOCATION_TYPES
from utils.helpers.contants import SUPPORTED_RAID_TYPES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.with_str_slash_option(
    "new_raid_type",
    "The new raid type (leave empty for no change!)",
    default=None,
    choices=[raid_type for raid_type in SUPPORTED_RAID_TYPES],
)
@tanjun.with_str_slash_option(
    "new_location", "The new location (leave empty for no change!)", default=None, autocomplete=autocomplete_location
)
@tanjun.with_str_slash_option(
    "new_boss", "The new boss to fight (leave empty for no change!)", default=None, autocomplete=autocomplete_pokemon
)
@tanjun.with_str_slash_option("raid_id", "The ID of the raid to edit", autocomplete=autocomplete_raid_id)
@tanjun.as_slash_command("edit", "Edit an existing raid.")
async def command_raid_edit(
    ctx: tanjun.abc.SlashContext,
    raid_id: str,
    new_boss: str | None,
    new_location: str | None,
    new_raid_type: str | None,
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
        response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_not_creator_or_moderator.format(
            bot_name=BOT_NAME.capitalize()
        )
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_not_creator_or_moderator.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, bot_name=BOT_NAME.capitalize()
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return

    raid = bot_aware.raids.get(f"'{raid_id}'")

    if new_boss is not None:
        success, pokemon, pokemon_image = await bot.validate_pokemon(new_boss)
        if not success:
            response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_unknown_boss.format(boss_name=new_boss)
            await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
            if log_errors:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_unknown_boss.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                )
                await bot.log_from_ctx(ctx, db, log_response)
            return

    timeout = 120
    if new_location is not None:
        location_name = ""
        location_splitted = new_location.split(",")
        if len(location_splitted) == 1:
            location_name = f"'{location_splitted[0]}'"
            # GET LOCATION TYPE
            location_type_action_row = ctx.rest.build_action_row()
            for location_type in SUPPORTED_LOCATION_TYPES:
                location_type_action_row.add_button(hikari.ButtonStyle.PRIMARY, location_type.lower()).set_label(
                    location_type
                ).add_to_container()

            location_type_embed = hikari.Embed(
                title=SUPPORTED_LANGUAGES.get(language).raid_edit_embed_title_location_type,
                description=SUPPORTED_LANGUAGES.get(language).raid_edit_embed_description_location_type,
                colour=hikari.Colour(0x8BC683),
            )

            response_message = await ctx.edit_last_response(
                embed=location_type_embed, components=[location_type_action_row]
            )

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
        else:
            location_name = location_splitted[1].removeprefix(" ")
            location_name = f"'{location_name}'"
            location_type = f"'{location_splitted[0]}'"

        latitude = ""
        longitude = ""
        results = await db.get_location_info(ctx.get_guild(), location_type, location_name)
        if results is not None and results != []:
            latitude = results[0].get("latitude")
            longitude = results[0].get("longitude")

    if new_location is None:
        location_name = None
        location_type = None

    success = await raid.update_raid(
        new_boss=new_boss, new_location=location_name, new_location_type=location_type, new_type=new_raid_type
    )
    if not success:
        response = SUPPORTED_LANGUAGES.get(language).response_raid_edit_failed
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit_failed.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return

    response = SUPPORTED_LANGUAGES.get(language).response_raid_edit
    await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
    if log_raid_edit:
        log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_edit.format(
            datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
        )
        await bot.log_from_ctx(ctx, db, log_response)
