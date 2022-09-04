# IMPORTS
import os

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.autocomplete_callbacks import autocomplete_location
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


@tanjun.with_str_slash_option("location", "The location to get information about.", autocomplete=autocomplete_location)
@tanjun.as_slash_command("locations_info", "Get information about a specific location.")
async def command_locations_info(
    ctx: tanjun.abc.SlashContext,
    location: str,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup"]
    )
    (log_errors, log_location_info, *none,) = await db.get_guild_log_settings(
        ctx.get_guild(),
        settings=[
            "log_errors",
            "log_location_info",
        ],
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    location_name = ""
    location_splitted = location.split(",")
    if len(location_splitted) == 1:
        response = SUPPORTED_LANGUAGES.get(language).response_location_info_no_results
        await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_info_no_results.format(
                datetime=await bot.get_timestamp_aware(gmt),
                member=ctx.member,
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        location_name = location_splitted[1].removeprefix(" ")
        location_name = f"'{location_name}'"
        location_type = f"'{location_splitted[0]}'"

        results = await db.get_location_info(ctx.get_guild(), location_type, location_name)
        if results == []:
            response = SUPPORTED_LANGUAGES.get(language).response_location_info_no_results
            await ctx.create_followup(response, delete_after=auto_delete, embed=None, components=None)
            if log_errors:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_location_info_no_results.format(
                    datetime=await bot.get_timestamp_aware(gmt),
                    member=ctx.member,
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
