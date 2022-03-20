# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
# Logging
import logging
# Own Files
from utils.DatabaseHandler import DatabaseHandler
# Hikari
import hikari
import tanjun
# Database and .env
import os
from dotenv import load_dotenv
# Functionality
import datetime


load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")

# ------------------------------------------------------------------------- #
# BOT UTILS CLASS #
# ------------------------------------------------------------------------- #
class BotUtils:
    async def get_timestamp(self) -> datetime.datetime:
        return datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    # LOGGING
    async def log_from_ctx(self, ctx: tanjun.abc.Context, _db: DatabaseHandler, message: str) -> None:
        language, *none = await _db.get_guild_settings(ctx.get_guild(), settings=["language"])
        logs_channel_id, *none = await _db.get_guild_log_settings(ctx.get_guild(), settings=["logs_channel_id"])

        if logs_channel_id is None:
            return

        try:
            log_channel = await ctx.rest.fetch_channel(logs_channel_id)
            await log_channel.send(message)
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.logger.guild_log_channel").error(f"Unexpected error while trying to send log message to log channel for guild_id: {ctx.guild_id}! Got error: {e}")

    async def log_from_event(self, event: hikari.Event, _db: DatabaseHandler, message: str) -> None:
        guild = await event.app.rest.fetch_guild(event.guild_id)
        language, *none = await _db.get_guild_settings(guild, settings=["language"])
        logs_channel_id, *none = await _db.get_guild_log_settings(guild, settings=["logs_channel_id"])

        if logs_channel_id is None:
            return

        try:
            log_channel = await event.app.rest.fetch_channel(logs_channel_id)
            await log_channel.send(message)
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.logger.guild_log_channel").error(f"Unexpected error while trying to send log message to log channel for guild_id: {event.guild_id}! Got error: {e}")

    # EMBEDS 
    async def embed_to_user(self, guild: hikari.Guild, title: str, description: str) -> hikari.Embed:
        embed = (
            hikari.Embed(
                title=title,
                description=description,
            )
                .set_thumbnail()
                .set_author(name=guild.name, icon=guild.icon_url)
        )
        return embed

    # VALIDATIONS
    async def validate_id(self, id_to_check: str | int) -> bool:
        try:
            int(id_to_check)
            valid_id=True
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.validate_id").error(f"ID check failed! Given value can't be converted to type int!")
            valid_id=False
        return valid_id

    async def validate_channel_type(self, channel_to_check: hikari.InteractionChannel, type_to_check) -> bool:
        desired_type=True
        if not isinstance(channel_to_check, type_to_check):
            logging.getLogger(f"{BOT_NAME.lower()}.validate_channel_type").error(f"Channel type check failed! Given channel is not the same as desired instance!")
            desired_type=False
        return desired_type
        