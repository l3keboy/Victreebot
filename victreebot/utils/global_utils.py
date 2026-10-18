from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING, Tuple

import datetime
from zoneinfo import ZoneInfo
import lightbulb
import pokebase as pb
from pokebase import APIResource

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.languages import en
import hikari

if TYPE_CHECKING:
    from victreebot.core.bot import Bot


# ------------------------------------------------------------------------- #
# BOT UTILS CLASS #
# ------------------------------------------------------------------------- #
class GlobalUtils:
    _bot: Bot

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._auto_delete_tasks: list[asyncio.Task[None]] = []

    # region TIMESTAMPS
    async def get_timestamp(self) -> str:
        return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    async def get_timestamp_aware(self, timezone: str) -> datetime.datetime:
        timezone_zoneinfo = ZoneInfo(timezone)
        return datetime.datetime.now().astimezone(timezone_zoneinfo)

    async def change_timestamp_format(
        self, timestamp: str, current_datetime_format: str, wished_datetime_format: str
    ) -> str:
        timestamp_current = datetime.datetime.strptime(timestamp, current_datetime_format)
        timestamp_wished = datetime.datetime.strftime(timestamp_current, wished_datetime_format)
        return timestamp_wished

    # endregion

    # region AUTO DELETE
    async def determine_auto_delete(self, auto_delete: int | None) -> int:
        return auto_delete if auto_delete is not None else 5

    async def handle_auto_delete(
        self,
        channel_id: hikari.Snowflake | int,
        response_message_id: hikari.Snowflake | int,
        auto_delete: int,
        *,
        _background: bool = False,
    ) -> None:
        """Automatically delete a Victreebot message from the Discord channel."""
        if auto_delete <= 0:
            return

        # If this isn't already running in the background, spawn a background task and return
        if not _background:
            self._auto_delete_tasks.append(
                asyncio.create_task(
                    self.handle_auto_delete(channel_id, response_message_id, auto_delete, _background=True)
                )
            )
            return

        # The actual background behavior
        try:
            await asyncio.sleep(auto_delete)
            await self._bot.discord_service.delete_message(channel_id, response_message_id)
        except Exception:
            logging.getLogger(__name__).exception("Failed to auto-delete message %s:", response_message_id)

    # endregion

    # region LOGGING
    async def handle_log_message(self, bot: Bot, guild_id: hikari.Snowflake | int, message: str) -> None:
        guild_log_settings = await bot.database.get_guild_log_settings(guild_id)
        if guild_log_settings is None or guild_log_settings.logs_channel_id is None:
            return

        try:
            await bot.discord_service.create_message(int(guild_log_settings.logs_channel_id), message)
        except Exception as e:
            logging.getLogger(__name__).error(
                "Unexpected error while trying to send log message to log channel for "
                f"guild_id: {guild_id}! Got error: {e}"
            )

    # endregion

    # region EMBEDS
    async def embed_to_user(self, guild: hikari.Guild, title: str, description: str) -> hikari.Embed:
        embed = hikari.Embed(title=title, description=description).set_author(
            name=guild.name, icon=guild.make_icon_url()
        )
        return embed

    # endregion

    # region VALIDATIONS
    async def validate_id(self, id_to_check: str | int) -> bool:
        try:
            int(id_to_check)
            valid_id = True
        except Exception:
            logging.getLogger(__name__).error("ID check failed! Given value can't be converted to type int!")
            valid_id = False
        return valid_id

    async def validate_latitude_longitude_type(
        self, latitude: float | int | str, longitude: float | int | str
    ) -> Tuple[bool, bool]:
        valid_latitude, valid_longitude = False, False

        try:
            float(latitude)
            valid_latitude = True
        except Exception:
            logging.getLogger(__name__).error(
                "Latitude type check failed! Given latitude is not convertable to type float!"
            )

        try:
            float(longitude)
            valid_longitude = True
        except Exception:
            logging.getLogger(__name__).error(
                "Longitude type check failed! Given longitude is not convertable to type float!"
            )
        return valid_latitude, valid_longitude

    async def validate_latitude_longitude_range(
        self, latitude: float | int | str, longitude: float | int | str
    ) -> Tuple[bool, bool]:
        valid_latitude, valid_longitude = False, False

        if float(latitude) >= -90 and float(latitude) <= 90:
            valid_latitude = True
        else:
            logging.getLogger(__name__).error("Latitude range check failed! Given latitude is not in the right range!")

        if float(longitude) >= -180 and float(longitude) <= 180:
            valid_longitude = True
        else:
            logging.getLogger(__name__).error(
                "Longitude range check failed! Given longitude is not in the right range!"
            )
        return valid_latitude, valid_longitude

    async def validate_channel_type(self, channel_to_check: object, type_to_check: type[object]) -> bool:
        desired_type = True
        if not isinstance(channel_to_check, type_to_check):
            logging.getLogger(__name__).error(
                "Channel type check failed! Given channel is not the same as desired instance!"
            )
            desired_type = False
        return desired_type

    async def validate_friend_code(self, friend_code: str) -> bool:
        friend_code_regex = r"^\d{4}\ \d{4}\ \d{4}$"
        if re.match(friend_code_regex, friend_code):
            return True
        else:
            logging.getLogger(__name__).error(
                "Friend code check failed! Given friend code is not in the correct format!"
            )
            return False

    async def validate_pokemon(self, pokemon: str | int) -> Tuple[bool, APIResource | None, str | None]:
        success = False
        pb_pokemon = None
        pokemon_image = None
        if isinstance(pokemon, str):
            try:
                pb_pokemon = pb.pokemon(str(pokemon.lower()))
                pokemon_image = pb.SpriteResource("pokemon", pb_pokemon.id).url
                success = True
            except Exception as e:
                pb_pokemon = None
                logging.getLogger(__name__).error(
                    f"Pokémon validation failed! Given pokémmon is not found! Got error: {e}!"
                )
        else:
            try:
                pb_pokemon = pb.pokemon(int(pokemon))
                pokemon_image = pb.SpriteResource("pokemon", pb_pokemon.id).url
                success = True
            except Exception as e:
                pb_pokemon = None
                logging.getLogger(__name__).error(
                    f"Pokémon validation failed! Given pokémmon is not found! Got error: {e}!"
                )
        return success, pb_pokemon, pokemon_image

    async def validate_timestamp_format(self, time: str, time_format: str) -> bool:
        desired_format = False
        try:
            if datetime.datetime.strptime(time, time_format):
                desired_format = True
        except ValueError as e:
            logging.getLogger(__name__).error(
                f"Timestamp check failed! Most likely to broad timestamp, f.e. 2:70! Got error: {e}"
            )
            desired_format = False
        return desired_format

    async def validate_enable_or_disable(self, ctx: lightbulb.Context, bot: Bot, item: str) -> tuple[bool, bool]:
        if ctx.guild_id is None:
            return False, True

        guild_settings = await bot.database.get_guild_settings(ctx.guild_id)
        if guild_settings is None:
            return False, True

        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)

        timeout = 60
        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.validate_enable_or_disable.format(item=item)
                    ),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.validate_enable_or_disable_description.format(item=item)
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.DANGER,
                                label=language_helper.disable,
                                custom_id="settings,disable",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.SUCCESS,
                                label=language_helper.enable,
                                custom_id="settings,enable",
                            ),
                        ]
                    ),
                ],
            )
        ]

        response_message = await ctx.respond(components=components)

        enable = False
        timeout_cancelled = False
        listening = True
        while listening:
            try:
                event = await bot.wait_for(
                    hikari.ComponentInteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: event.interaction.user.id == ctx.user.id,
                )

                command, action = event.interaction.custom_id.split(",")
                if command != "settings":
                    return False, True

                await event.interaction.create_initial_response(6)

                await bot.discord_service.delete_message(ctx.channel_id, response_message)
                if action == "enable":
                    enable = True
                    return enable, timeout_cancelled
                elif action == "disable":
                    return enable, timeout_cancelled

            except TimeoutError:
                await ctx.delete_response(response_message)
                return False, True
            except Exception:
                logging.getLogger(__name__).exception("An error occurred while listening for the info command!")
                await ctx.delete_response(response_message)
                return False, True
        return False, True

    async def validate_add_or_no_add(
        self, ctx: lightbulb.Context, bot: Bot, item: str
    ) -> Tuple[hikari.ComponentInteractionCreateEvent | None, bool]:
        if ctx.guild_id is None:
            return None, True

        guild_settings = await bot.database.get_guild_settings(ctx.guild_id)
        if guild_settings is None:
            return None, True

        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)

        timeout = 60
        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.validate_add_or_no_add.format(item=item)
                    ),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.validate_add_or_no_add_description.format(item=item)
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.DANGER, label=language_helper.no, custom_id="validate,no_add"
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.SUCCESS, label=language_helper.yes, custom_id="validate,add"
                            ),
                        ]
                    ),
                ],
            )
        ]

        response_message = await ctx.respond(components=components)

        add = False
        listening = True
        while listening:
            try:
                event = await bot.wait_for(
                    hikari.ComponentInteractionCreateEvent,
                    timeout=timeout,
                    predicate=lambda event: event.interaction.user.id == ctx.user.id,
                )

                command, action = event.interaction.custom_id.split(",")
                if command != "validate":
                    return None, True

                await bot.discord_service.delete_message(ctx.channel_id, response_message)
                if action == "add":
                    add = True
                    return event, add
                elif action == "no_add":
                    return event, add

            except TimeoutError:
                await ctx.delete_response(response_message)
                return None, False
            except Exception:
                logging.getLogger(__name__).exception("An error occurred while listening for the info command!")
                await ctx.delete_response(response_message)
                return None, False
        return None, False

    # endregion
