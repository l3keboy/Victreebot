import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.utils.shared_autocompletes import autocomplete_locations
from victreebot.languages import en

# Load command
loader = lightbulb.Loader()


# Command
@loader.command
class LocationsInfo(
    lightbulb.SlashCommand, 
    name="locations_info", 
    description="Get information about a specific location",
):
    """Command to get info about a pokemon."""

    location: str = lightbulb.string(
        "location",
        "The location to get information about.",
        autocomplete=autocomplete_locations,  # type: ignore[arg-type]  # mypy: ignore
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

        # Create language helper
        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
        auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)

        if not guild_settings.is_setup:
            response_message = await ctx.respond(language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize()))
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        location_name = ""
        location_splitted = self.location.split(",")
        if len(location_splitted) == 1:
            response_message = await ctx.respond(language_helper.response_location_info_no_results)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_location_info_no_results.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return
        else:
            location_name = location_splitted[1].removeprefix(" ")
            location_name = f"{location_name}"
            location_type = f"{location_splitted[0]}"

            location = await bot.database.get_location(ctx.guild_id, location_type, location_name)
            if location is None:
                response_message = await ctx.respond(language_helper.response_location_info_no_results)
                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_location_info_no_results.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return

            known_coordinates = "[{google_maps_translation}](https://www.google.com/maps/place/{latitude},{longitude})"
            unknown_coordinates = f"`{language_helper.location_no_coordinates_set}`"

            components = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.location_info_embed_title),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=f"""`{location_type.capitalize().strip("'")}:` {location_name.capitalize().strip("'")}\n `Description:` {location.description if location.description else language_helper.location_no_description_set}"""
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.location_info_embed_field_coordinates),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=f"Latitude: {'`'+str(location.latitude)+'`' if location.latitude else unknown_coordinates}\n Longitude: {'`'+str(location.longitude)+'`' if location.longitude else unknown_coordinates}"
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.location_info_embed_field_google_maps),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=f"{known_coordinates.format(google_maps_translation=language_helper.location_google_maps, latitude=str(location.latitude), longitude=str(location.longitude)) if location.latitude is not None and location.longitude is not None else unknown_coordinates}"
                        ),
                    ]
                )
            ]

            auto_delete_helper = 20 if auto_delete_helper < 20 else auto_delete_helper
            response_message = await ctx.respond(components=components)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_info:
                log_response = language_helper.log_response_location_info_requested.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member, location_type=location_type.strip("'"),
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
