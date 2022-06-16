# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import asyncio
import datetime
import logging
import os
from typing import Tuple

import hikari
import pytz
import tanjun
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.contants import SUPPORTED_LANGUAGES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# BOT UTILS CLASS #
# ------------------------------------------------------------------------- #
class BotUtils:
    async def get_timestamp(self) -> datetime.datetime:
        return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    async def get_timestamp_aware(self, gmt: str) -> datetime.datetime:
        if "-" in gmt:
            gmt_inverted = gmt.replace("-", "+")
        if "+" in gmt:
            gmt_inverted = gmt.replace("+", "-")
        timezone = pytz.timezone(f"Etc/{gmt_inverted}")
        return datetime.datetime.now().astimezone(timezone)

    # LOGGING
    async def log_from_ctx(self, ctx: tanjun.abc.SlashContext, db: DatabaseHandler, message: str) -> None:
        language, *none = await db.get_guild_settings(ctx.get_guild(), settings=["language"])
        logs_channel_id, *none = await db.get_guild_log_settings(ctx.get_guild(), settings=["logs_channel_id"])
        if logs_channel_id is None:
            return
        try:
            log_channel = ctx.cache.get_guild_channel(logs_channel_id) or await ctx.rest.fetch_channel(logs_channel_id)
            await log_channel.send(message)
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.logger.guild_log_channel").error(
                "Unexpected error while trying to send log message to log channel for "
                f"guild_id: {ctx.guild_id}! Got error: {e}"
            )

    async def log_from_event(self, event: hikari.Event, db: DatabaseHandler, message: str) -> None:
        guild = event.app.cache.get_guild(event.guild_id) or await event.app.rest.fetch_guild(event.guild_id)
        language, *none = await db.get_guild_settings(guild, settings=["language"])
        logs_channel_id, *none = await db.get_guild_log_settings(guild, settings=["logs_channel_id"])
        if logs_channel_id is None:
            return
        try:
            log_channel = event.app.cache.get_guild_channel(logs_channel_id) or await event.app.rest.fetch_channel(
                logs_channel_id
            )
            await log_channel.send(message)
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.logger.guild_log_channel").error(
                "Unexpected error while trying to send log message to log channel for "
                f"guild_id: {event.guild_id}! Got error: {e}"
            )

    # EMBEDS
    async def embed_to_user(self, guild: hikari.Guild, title: str, description: str) -> hikari.Embed:
        embed = hikari.Embed(
            title=title,
            description=description,
        ).set_author(name=guild.name, icon=guild.icon_url)
        return embed

    # VALIDATIONS
    async def validate_id(self, id_to_check: str | int) -> bool:
        try:
            int(id_to_check)
            valid_id = True
        except Exception:
            logging.getLogger(f"{BOT_NAME.lower()}.validate_id").error(
                "ID check failed! Given value can't be converted to type int!"
            )
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
            logging.getLogger(f"{BOT_NAME.lower()}.validate_latitude_longitude_type").error(
                "Latitude type check failed! Given latitude is not convertable to type float!"
            )

        try:
            float(longitude)
            valid_longitude = True
        except Exception:
            logging.getLogger(f"{BOT_NAME.lower()}.validate_latitude_longitude_type").error(
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
            logging.getLogger(f"{BOT_NAME.lower()}.validate_latitude_longitude_range").error(
                "Latitude range check failed! Given latitude is not in the right range!"
            )

        if float(longitude) >= -180 and float(longitude) <= 180:
            valid_longitude = True
        else:
            logging.getLogger(f"{BOT_NAME.lower()}.validate_latitude_longitude_range").error(
                "Longitude range check failed! Given longitude is not in the right range!"
            )
        return valid_latitude, valid_longitude

    async def validate_channel_type(self, channel_to_check: hikari.InteractionChannel, type_to_check) -> bool:
        desired_type = True
        if not isinstance(channel_to_check, type_to_check):
            logging.getLogger(f"{BOT_NAME.lower()}.validate_channel_type").error(
                "Channel type check failed! Given channel is not the same as desired instance!"
            )
            desired_type = False
        return desired_type

    async def validate_enable_or_disable(self, ctx: tanjun.abc.SlashContext, item: str, db: DatabaseHandler) -> bool:
        language, auto_delete, *none = await db.get_guild_settings(
            guild=ctx.get_guild(), settings=["language", "auto_delete"]
        )

        timeout = 60
        embed = hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).validate_enable_or_disable.format(item=item),
            description=SUPPORTED_LANGUAGES.get(language).validate_enable_or_disable_description.format(item=item),
        )

        action_row = (
            ctx.rest.build_action_row()
            .add_button(hikari.ButtonStyle.DANGER, "disable")
            .set_label(SUPPORTED_LANGUAGES.get(language).disable)
            .add_to_container()
            .add_button(hikari.ButtonStyle.SUCCESS, "enable")
            .set_label(SUPPORTED_LANGUAGES.get(language).enable)
            .add_to_container()
        )

        response_message = await ctx.create_followup(embed=embed, component=action_row)

        enable = False
        try:
            event = await ctx.client.events.wait_for(
                hikari.InteractionCreateEvent,
                timeout=timeout,
                predicate=lambda event: event.interaction.user.id == ctx.author.id
                and event.interaction.message.id == response_message.id,
            )
        except asyncio.TimeoutError:
            await ctx.edit_last_response(
                SUPPORTED_LANGUAGES.get(language).enable_disable_timeout, delete_after=auto_delete
            )
            return event, enable
        else:
            await response_message.delete()
            if event.interaction.custom_id == "enable":
                enable = True
                return event, enable
            elif event.interaction.custom_id == "disable":
                return event, enable

    async def validate_add_or_no_add(self, ctx: tanjun.abc.SlashContext, item: str, db: DatabaseHandler) -> Tuple[hikari.InteractionCreateEvent, bool]:
        language, auto_delete, *none = await db.get_guild_settings(
            guild=ctx.get_guild(), settings=["language", "auto_delete"]
        )

        timeout = 60
        embed = hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).validate_add_or_no_add.format(item=item),
            description=SUPPORTED_LANGUAGES.get(language).validate_add_or_no_add_description.format(item=item),
        )

        action_row = (
            ctx.rest.build_action_row()
            .add_button(hikari.ButtonStyle.DANGER, "no_add")
            .set_label(SUPPORTED_LANGUAGES.get(language).no)
            .add_to_container()
            .add_button(hikari.ButtonStyle.SUCCESS, "add")
            .set_label(SUPPORTED_LANGUAGES.get(language).yes)
            .add_to_container()
        )

        response_message = await ctx.create_followup(embed=embed, component=action_row)

        add = False
        try:
            event = await ctx.client.events.wait_for(
                hikari.InteractionCreateEvent,
                timeout=timeout,
                predicate=lambda event: event.interaction.user.id == ctx.author.id
                and event.interaction.message.id == response_message.id,
            )
        except asyncio.TimeoutError:
            await ctx.edit_last_response(SUPPORTED_LANGUAGES.get(language).add_no_add_timeout, delete_after=auto_delete)
            return event, add
        else:
            await response_message.delete()
            if event.interaction.custom_id == "add":
                add = True
                return event, add
            elif event.interaction.custom_id == "no_add":
                return event, add
