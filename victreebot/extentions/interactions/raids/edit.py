# IMPORTS
import asyncio
import os
import datetime
import pytz
import hikari
import tanjun
from core.bot import Bot
from dateutil.rrule import *  # noqa F403
import time
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
    "change_date_time",
    "The the date and time of a raid (Leave empty or no for no change)",
    default=None,
    choices=["Yes", "No"],
)
@tanjun.with_str_slash_option(
    "new_raid_type",
    "Change the raid type",
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
    change_date_time: str | None,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    (
        language,
        auto_delete,
        gmt,
        is_setup,
        moderator_role_id,
        extended_time_format,
        raid_timeout,
        *none,
    ) = await db.get_guild_settings(
        guild=ctx.get_guild(),
        settings=[
            "language",
            "auto_delete",
            "gmt",
            "is_setup",
            "moderator_role_id",
            "extended_time_format",
            "raid_timeout",
        ],
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

    if ctx.author.id != raid.raid_creator_id and moderator_role_id not in ctx.member.role_ids:
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
        if new_boss != "egg1" and new_boss != "egg3" and new_boss != "egg5" and new_boss != "eggmega":
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
            location_name = location_splitted[0].replace("'", "''")
            location_name = f"'{location_name}'"
            # GET LOCATION TYPE
            location_type_action_row = ctx.rest.build_message_action_row()
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
            location_name = location_name.replace("'", "''")
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

    end_time = None
    raid_takes_place_at_to_show = None
    raid_takes_place_at = None
    if change_date_time is not None and change_date_time != "No":
        if "-" in gmt:
            gmt_inverted = gmt.replace("-", "+")
        if "+" in gmt:
            gmt_inverted = gmt.replace("+", "-")
        timezone = pytz.timezone(f"Etc/{gmt_inverted}")

        timezone_aware_current_date = datetime.datetime.today().astimezone(timezone).date()
        days = rrule(DAILY, dtstart=timezone_aware_current_date)  # noqa F405

        date_action_row = ctx.rest.build_message_action_row().add_select_menu(hikari.ComponentType.TEXT_SELECT_MENU, "date")
        for day in days[:24]:
            date_action_row.add_option(
                f"{SUPPORTED_LANGUAGES.get(language).weekdays[day.weekday()]} {day.day} "
                f"{SUPPORTED_LANGUAGES.get(language).months[day.month - 1]}",
                str(day),
            ).add_to_menu()
        date_action_row = date_action_row.add_to_container()

        time_action_row = (
            ctx.rest.build_modal_action_row()
            .add_text_input(
                label=SUPPORTED_LANGUAGES.get(language).raid_create_modal_time_text_input,
                custom_id="location_name",
            )
            .set_placeholder(SUPPORTED_LANGUAGES.get(language).raid_create_modal_time_text_input_placeholder)
            .set_required(True)
            .add_to_container()
        )

        date_embed = hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).raid_create_embed_title_date,
            description=SUPPORTED_LANGUAGES.get(language).raid_create_embed_description_date,
            colour=hikari.Colour(0x8BC683),
        )

        response_message = await ctx.edit_last_response(embed=date_embed, components=[date_action_row])

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
            raid_date = event.interaction.values[0]
            await event.interaction.create_modal_response(
                SUPPORTED_LANGUAGES.get(language).raid_create_modal_time,
                "raid_create_modal_time",
                components=[time_action_row],
            )
            try:
                event = await ctx.client.events.wait_for(
                    hikari.InteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
                    and event.interaction.user.id == ctx.author.id,
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
                await event.interaction.create_initial_response(6)
                if event.interaction.custom_id == "raid_create_modal_time":
                    if event.interaction.components[0][0].value is not None:
                        raid_time = event.interaction.components[0][0].value
                        valid_time = await bot.validate_timestamp_format(raid_time, "%H:%M")
                        if not valid_time:
                            response = SUPPORTED_LANGUAGES.get(language).response_raid_create_invalid_time
                            await ctx.edit_last_response(
                                response, delete_after=auto_delete, embed=None, components=None
                            )
                            if log_errors:
                                log_response = SUPPORTED_LANGUAGES.get(
                                    language
                                ).log_response_raid_create_invalid_time.format(
                                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                                )
                                await bot.log_from_ctx(ctx, db, log_response)
                            return

        raid_date = await bot.change_timestamp_format(raid_date, "%Y-%m-%d %H:%M:%S", "%d/%m/%Y")
        raid_takes_place_at = f"{raid_date} {raid_time}"

        if extended_time_format:
            raid_takes_place_at_to_show = f"{raid_date} {raid_time} {gmt}"
        else:
            raid_takes_place_at_to_show = f"{raid_time}"

        raid_takes_place_at_server_timezone_aware = datetime.datetime.strptime(
            str(raid_takes_place_at), "%d/%m/%Y %H:%M"
        ).replace(tzinfo=timezone)
        datetime_obj_now_utc = datetime.datetime.now().astimezone(tz=pytz.UTC)
        datetime_obj_raid_takes_place_at_utc = raid_takes_place_at_server_timezone_aware.astimezone(tz=pytz.UTC)

        if datetime_obj_raid_takes_place_at_utc < datetime_obj_now_utc:
            response = SUPPORTED_LANGUAGES.get(language).response_raid_create_date_time_already_past
            await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
            if log_errors:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_create_date_time_already_past.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                )
                await bot.log_from_ctx(ctx, db, log_response)
            return

        difference = datetime_obj_raid_takes_place_at_utc - datetime_obj_now_utc
        end_time = time.time() + difference.total_seconds() + int(raid_timeout)

    success = await raid.update_raid(
        new_boss=new_boss,
        new_location=location_name,
        new_location_type=location_type,
        new_type=new_raid_type,
        new_end_time=end_time,
        new_raid_takes_place_at_to_show=raid_takes_place_at_to_show,
        new_raid_takes_place_at=raid_takes_place_at,
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
