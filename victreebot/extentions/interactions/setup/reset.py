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
import logging
from pathlib import Path

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")
SUPPORT_SERVER_LINK = os.getenv("SUPPORT_SERVER_LINK")
BOT_INVITE_LINK = os.getenv("BOT_INVITE_LINK")

# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.with_author_permission_check(
    hikari.Permissions.MANAGE_GUILD,
    error_message="You need the `Manage Guild` permissions to execute this command!",
)
@tanjun.as_slash_command("reset", f"Reset {BOT_NAME.capitalize()}")
async def command_reset(
    ctx: tanjun.abc.SlashContext,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup"]
    )
    log_errors, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=5)
        return

    timeout = 120
    embed = hikari.Embed(
        title=SUPPORTED_LANGUAGES.get(language).reset_validation_embed_title.format(bot_name=BOT_NAME.capitalize()),
        description=SUPPORTED_LANGUAGES.get(language).reset_validation_embed_description.format(bot_name=BOT_NAME.capitalize()),
    )

    action_row_1 = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.SUCCESS, "yes")
        .set_label(SUPPORTED_LANGUAGES.get(language).yes)
        .add_to_container()
        .add_button(hikari.ButtonStyle.DANGER, "no")
        .set_label(SUPPORTED_LANGUAGES.get(language).no)
        .add_to_container()
    )

    response_message = await ctx.respond(embed, components=[action_row_1])

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ComponentInteraction)
            and event.interaction.user.id == ctx.author.id
            and event.interaction.message.id == response_message.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_reset_timeout_reached
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_reset_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, bot_name=BOT_NAME.capitalize(),
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        await event.interaction.create_initial_response(6)
        if event.interaction.custom_id == "yes":
            gif = Path("../Husqy/assets/loading.gif")
            embed_started = (
                hikari.Embed(
                    title=SUPPORTED_LANGUAGES.get(language).reset_started_embed_title.format(bot_name=BOT_NAME.capitalize()),
                    description=SUPPORTED_LANGUAGES.get(language).reset_started_embed_description.format(bot_name=BOT_NAME.capitalize()),
                    colour=hikari.Colour(0x8bc683),
                )
                .set_thumbnail(gif)
            )
            response_message = await ctx.edit_last_response(embed=embed_started, component=None)

            guild = ctx.get_guild()
            my_user = await ctx.rest.fetch_my_user()

            # DELETE CUSTOM EMOJI'S
            all_server_emojis = await ctx.rest.fetch_guild_emojis(guild)
            for emoji in all_server_emojis:
                if emoji.name == "Instinct" or emoji.name == "Mystic" or emoji.name == "Valor":
                    try:
                        await ctx.rest.delete_emoji(
                            guild, emoji.id, reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Redo setup!"
                        )
                        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").info(
                            f"Deleted emoji with same name ('Instinct', 'Mystic' or 'Valor') for guild_id: {ctx.guild_id}!"
                        )
                    except hikari.ForbiddenError:
                        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").error(
                            "ForbiddenError while trying to delete emoji with same name ('Instinct', 'Mystic' or 'Valor') "
                            f"for guild_id: {ctx.guild_id}!"
                        )
                    except Exception as e:
                        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").error(
                            "Unexpected error while trying to delete emoji with same name ('Instinct', 'Mystic' or 'Valor') "
                            f"for guild_id: {ctx.guild_id}! Got error: {e}"
                        )

            # DELETE ROLES
            all_server_roles = await ctx.rest.fetch_roles(guild)
            for role in all_server_roles:
                if role.name == "Instinct":
                    await ctx.rest.delete_role(guild, role)
                if role.name == "Mystic":
                    await ctx.rest.delete_role(guild, role)
                if role.name == "Valor":
                    await ctx.rest.delete_role(guild, role)
                if role.name == f"{BOT_NAME.capitalize()} moderator":
                    await ctx.rest.delete_role(guild, role)

            # DELETE CHANNELS
            channel_raids = await db.get_guild_settings(guild, settings=["raids_channel_id"])
            channel_logs = await db.get_guild_log_settings(guild, settings=["logs_channel_id"])
            await ctx.rest.delete_channel(channel_raids)
            await ctx.rest.delete_channel(channel_logs)

            await db.set_guild_setting(guild, parameters=["is_setup = false", f"raids_channel_id = NULL"])
            await db.set_guild_log_setting(guild, parameters=[f"logs_channel_id = NULL"])

            embed_finished = (
                hikari.Embed(
                    title=SUPPORTED_LANGUAGES.get(language).reset_finished_embed_title.format(bot_name=BOT_NAME.capitalize()),
                    description=SUPPORTED_LANGUAGES.get(language).reset_finished_embed_description.format(bot_name=BOT_NAME.capitalize()),
                    colour=hikari.Colour(0x8bc683),
                )
            )
            await response_message.delete()
            response_message = await ctx.rest.create_message(ctx.get_channel(), embed=embed_finished)
            await asyncio.sleep(10)
            await response_message.delete()
        elif event.interaction.custom_id == "no":
            response = SUPPORTED_LANGUAGES.get(language).response_reset_cancelled.format(bot_name=BOT_NAME.capitalize())
            await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
            if log_errors:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_reset_cancelled.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, bot_name=BOT_NAME.capitalize(),
                )
                await bot.log_from_ctx(ctx, db, log_response)
            return