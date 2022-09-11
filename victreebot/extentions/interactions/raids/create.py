# IMPORTS
import asyncio
import datetime
import os
import time
import uuid
from pathlib import Path

import hikari
import pytz
import tanjun
from core.bot import Bot
from dateutil.rrule import *  # noqa F403
from dotenv import load_dotenv
from extentions.interactions.raids.RaidClass import RaidClass
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.autocomplete_callbacks import autocomplete_location
from utils.helpers.autocomplete_callbacks import autocomplete_pokemon
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES
from utils.helpers.contants import SUPPORTED_LOCATION_TYPES
from utils.helpers.contants import SUPPORTED_RAID_TYPES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# FUNCTIONS #
# ------------------------------------------------------------------------- #
async def generate_check_id(db: DatabaseHandler):
    raid_id_uuid = f"{uuid.uuid4()}"[:6]
    raid_id = f"'{raid_id_uuid}'"

    ids_to_check = []
    all_raid_ids = await db.get_distinct("raid_id", "Raids")
    for existing_raid_id in all_raid_ids[0]:
        ids_to_check.append(existing_raid_id.get("raid_id"))

    if raid_id_uuid in ids_to_check:
        await generate_check_id(db)
    else:
        return raid_id


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.with_str_slash_option("location", "The location the raid takes place.", autocomplete=autocomplete_location)
@tanjun.with_str_slash_option("boss", "The boss to fight.", autocomplete=autocomplete_pokemon)
@tanjun.as_slash_command("create", "Create a raid.")
async def command_raid_create(
    ctx: tanjun.abc.SlashContext,
    location: str,
    boss: str,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    (
        language,
        auto_delete,
        gmt,
        is_setup,
        channel_raids,
        raid_timeout,
        extended_time_format,
        *none,
    ) = await db.get_guild_settings(
        guild=ctx.get_guild(),
        settings=[
            "language",
            "auto_delete",
            "gmt",
            "is_setup",
            "raids_channel_id",
            "raid_timeout",
            "extended_time_format",
        ],
    )
    log_errors, log_raid_create, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_raid_create"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    timeout = 120

    # GET RAID TYPE
    raid_type_action_row = ctx.rest.build_action_row()
    for raid_type in SUPPORTED_RAID_TYPES:
        raid_type_action_row.add_button(hikari.ButtonStyle.PRIMARY, raid_type.lower()).set_label(
            raid_type
        ).add_to_container()

    raid_type_embed = hikari.Embed(
        title=SUPPORTED_LANGUAGES.get(language).raid_create_embed_title_raid_type,
        description=SUPPORTED_LANGUAGES.get(language).raid_create_embed_description_raid_type,
        colour=hikari.Colour(0x8BC683),
    )

    response_message = await ctx.respond(embed=raid_type_embed, components=[raid_type_action_row])

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
        await event.interaction.create_initial_response(6)
        raid_type = event.interaction.custom_id

        if boss != "egg1" and boss != "egg3" and boss != "egg5" and boss != "eggmega":
            success, pokemon, pokemon_image = await bot.validate_pokemon(boss)
            pokemon_name = pokemon.name
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_raid_create_unknown_boss.format(boss_name=boss)
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_create_unknown_boss.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return
        else:
            path = Path().resolve()
            pokemon = boss
            pokemon_name = boss
            if boss == "egg1":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggOne.png"
            elif boss == "egg3":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggThree.png"
            elif boss == "egg5":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggFive.png"
            elif boss == "eggmega":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggMega.png"

    location_name = ""
    location_splitted = location.split(",")
    if len(location_splitted) == 1:
        location_name = f"'{location_splitted[0]}'"
        # GET LOCATION TYPE
        location_type_action_row = ctx.rest.build_action_row()
        for location_type in SUPPORTED_LOCATION_TYPES:
            location_type_action_row.add_button(hikari.ButtonStyle.PRIMARY, location_type.lower()).set_label(
                location_type
            ).add_to_container()

        location_type_embed = hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).raid_create_embed_title_location_type,
            description=SUPPORTED_LANGUAGES.get(language).raid_create_embed_description_location_type,
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

    if "-" in gmt:
        gmt_inverted = gmt.replace("-", "+")
    if "+" in gmt:
        gmt_inverted = gmt.replace("+", "-")
    timezone = pytz.timezone(f"Etc/{gmt_inverted}")

    timezone_aware_current_date = datetime.datetime.today().astimezone(timezone).date()
    days = rrule(DAILY, dtstart=timezone_aware_current_date)  # noqa F405

    # GET RAID TIME
    date_action_row = ctx.rest.build_action_row().add_select_menu("date")
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
            label=SUPPORTED_LANGUAGES.get(language).raid_create_modal_time_text_input.format(
                location=location_type.strip("'")
            ),
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
            SUPPORTED_LANGUAGES.get(language).raid_create_modal_time.format(
                location=location_type.strip("'").capitalize()
            ),
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
                        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
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

    raid_id = await generate_check_id(db)

    difference = datetime_obj_raid_takes_place_at_utc - datetime_obj_now_utc
    end_time = time.time() + difference.total_seconds() + int(raid_timeout)

    channel_raids = ctx.cache.get_guild_channel(channel_raids) or await ctx.rest.fetch_channel(channel_raids)

    embed = (
        hikari.Embed(
            description=SUPPORTED_LANGUAGES.get(language).raid_embed_description_with_location_link.format(
                raid_id=raid_id.strip("'"),
                raid_type=raid_type.capitalize(),
                time_date=f"""{raid_takes_place_at_to_show.strip("'")}""",
                location=location_name.capitalize().strip("'"),
                latitude=latitude,
                longitude=longitude,
            )
            if latitude is not None and latitude != ""
            else SUPPORTED_LANGUAGES.get(language).raid_embed_description_without_location_link.format(
                raid_id=raid_id.strip("'"),
                raid_type=raid_type.capitalize(),
                time_date=f"""{raid_takes_place_at_to_show.strip("'")}""",
                location=location_name.capitalize().strip("'"),
            ),
            colour=hikari.Colour(0x8BC683),
        )
        .set_thumbnail(pokemon_image)
        .set_author(name=pokemon_name.replace("-", " ").capitalize(), icon=pokemon_image)
        .set_footer(
            text=SUPPORTED_LANGUAGES.get(language).raid_embed_footer.format(
                member=ctx.member.display_name, attendees="0"
            )
        )
        .add_field("Instinct:", value="\u200b", inline=False)
        .add_field("Mystic:", value="\u200b", inline=False)
        .add_field("Valor:", value="\u200b", inline=False)
        .add_field("Remote:", value="\u200b", inline=False)
    )

    raid_message = await channel_raids.send(embed=embed)

    instinct_emoji_id, mystic_emoji_id, valor_emoji_id, *none = await db.get_guild_settings(
        ctx.get_guild(), settings=["instinct_emoji_id", "mystic_emoji_id", "valor_emoji_id"]
    )
    instinct_emoji = ctx.cache.get_emoji(instinct_emoji_id) or await ctx.rest.fetch_emoji(
        ctx.get_guild(), instinct_emoji_id
    )
    mystic_emoji = ctx.cache.get_emoji(mystic_emoji_id) or await ctx.rest.fetch_emoji(ctx.get_guild(), mystic_emoji_id)
    valor_emoji = ctx.cache.get_emoji(valor_emoji_id) or await ctx.rest.fetch_emoji(ctx.get_guild(), valor_emoji_id)
    one_emoji = "1️⃣"
    two_emoji = "2️⃣"
    three_emoji = "3️⃣"
    remote_emoji = "🇷"
    await raid_message.add_reaction(instinct_emoji)
    await raid_message.add_reaction(mystic_emoji)
    await raid_message.add_reaction(valor_emoji)
    await raid_message.add_reaction(one_emoji)
    await raid_message.add_reaction(two_emoji)
    await raid_message.add_reaction(three_emoji)
    await raid_message.add_reaction(remote_emoji)

    RaidClass(
        raid_id,
        raid_type,
        location_type,
        location_name,
        raid_takes_place_at,
        raid_takes_place_at_to_show,
        pokemon_name.lower(),
        ctx.get_guild(),
        end_time,
        channel_raids.id,
        raid_message.id,
        ctx.member.id,
        bot,
        bot_aware,
        language,
        auto_delete,
    )

    raids_created, *none = await db.get_guild_stats(ctx.get_guild(), stats=["raids_created"])
    new_raids_created = int(raids_created) + 1
    await db.set_guild_stats(ctx.get_guild(), parameters=[f"raids_created = {new_raids_created}"])

    stats_raids_created, *none = await db.get_user_details(ctx.get_guild(), ctx.member, details=["stats_raids_created"])
    new_stats_raids_created = int(stats_raids_created) + 1
    await db.set_user_detail(
        ctx.get_guild(), ctx.member, parameters=[f"stats_raids_created = {new_stats_raids_created}"]
    )

    response = SUPPORTED_LANGUAGES.get(language).response_raid_create_success
    await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
    if log_raid_create:
        log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_create_success.format(
            datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
        )
        await bot.log_from_ctx(ctx, db, log_response)
