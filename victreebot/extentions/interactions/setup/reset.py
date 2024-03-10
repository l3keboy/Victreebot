# IMPORTS
import asyncio
import logging
import os
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
    language, auto_delete, gmt, is_setup, channel_raids, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup", "raids_channel_id"]
    )
    channel_logs, log_errors, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["logs_channel_id", "log_errors"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=5)
        return

    if ctx.channel_id == channel_raids or ctx.channel_id == channel_logs:
        response = SUPPORTED_LANGUAGES.get(language).response_reset_from_channel_not_possible
        await ctx.edit_last_response(response, delete_after=5)
        return

    timeout = 120
    embed = hikari.Embed(
        title=SUPPORTED_LANGUAGES.get(language).reset_validation_embed_title.format(bot_name=BOT_NAME.capitalize()),
        description=SUPPORTED_LANGUAGES.get(language).reset_validation_embed_description.format(
            bot_name=BOT_NAME.capitalize()
        ),
    )

    action_row_1 = (
        ctx.rest.build_message_action_row()
        .add_interactive_button(hikari.ButtonStyle.SUCCESS, "yes", label=SUPPORTED_LANGUAGES.get(language).yes)
        .add_interactive_button(hikari.ButtonStyle.DANGER, "no", label=SUPPORTED_LANGUAGES.get(language).no)
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
                datetime=await bot.get_timestamp_aware(gmt),
                member=ctx.member,
                bot_name=BOT_NAME.capitalize(),
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        await event.interaction.create_initial_response(6)
        if event.interaction.custom_id == "yes":
            gif = Path("./assets/gifs/loading.gif")
            embed_started = hikari.Embed(
                title=SUPPORTED_LANGUAGES.get(language).reset_started_embed_title.format(
                    bot_name=BOT_NAME.capitalize()
                ),
                description=SUPPORTED_LANGUAGES.get(language).reset_started_embed_description.format(
                    bot_name=BOT_NAME.capitalize()
                ),
                colour=hikari.Colour(0x8BC683),
            ).set_thumbnail(gif)
            response_message = await ctx.edit_last_response(embed=embed_started, component=None)

            guild = ctx.get_guild()

            # DELETE CUSTOM EMOJI'S
            try:
                instinct_emoji, *none = await db.get_guild_settings(guild, settings=["instinct_emoji_id"])
                await ctx.rest.delete_emoji(
                    guild, instinct_emoji, reason=f"{BOT_NAME.capitalize()} reset Handler -- Reset!"
                )
            except hikari.ForbiddenError:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.emojis_delete").error(
                    "ForbiddenError while trying to delete emoji with same name ('Instinct', 'Mystic' or 'Valor') "
                    f"for guild_id: {ctx.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.emojis_delete").error(
                    "Unexpected error while trying to delete instinct emoji "
                    f"for guild_id: {ctx.guild_id}! Got error: {e}"
                )

            try:
                mystic_emoji, *none = await db.get_guild_settings(guild, settings=["mystic_emoji_id"])
                await ctx.rest.delete_emoji(
                    guild, mystic_emoji, reason=f"{BOT_NAME.capitalize()} reset Handler -- Reset!"
                )
            except hikari.ForbiddenError:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.emojis_delete").error(
                    "ForbiddenError while trying to delete emoji with same name ('Instinct', 'Mystic' or 'Valor') "
                    f"for guild_id: {ctx.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.emojis_delete").error(
                    "Unexpected error while trying to delete mystic emoji "
                    f"for guild_id: {ctx.guild_id}! Got error: {e}"
                )

            try:
                valor_emoji, *none = await db.get_guild_settings(guild, settings=["valor_emoji_id"])
                await ctx.rest.delete_emoji(
                    guild, valor_emoji, reason=f"{BOT_NAME.capitalize()} reset Handler -- Reset!"
                )
            except hikari.ForbiddenError:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.emojis_delete").error(
                    "ForbiddenError while trying to delete emoji with same name ('Instinct', 'Mystic' or 'Valor') "
                    f"for guild_id: {ctx.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.emojis_delete").error(
                    "Unexpected error while trying to delete valor emoji "
                    f"for guild_id: {ctx.guild_id}! Got error: {e}"
                )

            # DELETE ROLES
            try:
                instinct_role, *none = await db.get_guild_settings(guild, settings=["instinct_role_id"])
                await ctx.rest.delete_role(guild, instinct_role)
            except hikari.ForbiddenError:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.roles_delete").error(
                    "ForbiddenError while trying to delete instinct role " f"for guild_id: {ctx.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.roles_delete").error(
                    "Unexpected error while trying to delete instinct role "
                    f"for guild_id: {ctx.guild_id}! Got error: {e}"
                )

            try:
                mystic_role, *none = await db.get_guild_settings(guild, settings=["mystic_role_id"])
                await ctx.rest.delete_role(guild, mystic_role)
            except hikari.ForbiddenError:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.roles_delete").error(
                    "ForbiddenError while trying to delete mystic role " f"for guild_id: {ctx.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.roles_delete").error(
                    "Unexpected error while trying to delete mystic role "
                    f"for guild_id: {ctx.guild_id}! Got error: {e}"
                )

            try:
                valor_role, *none = await db.get_guild_settings(guild, settings=["valor_role_id"])
                await ctx.rest.delete_role(guild, valor_role)
            except hikari.ForbiddenError:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.roles_delete").error(
                    "ForbiddenError while trying to delete valor role " f"for guild_id: {ctx.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.roles_delete").error(
                    "Unexpected error while trying to delete valor role "
                    f"for guild_id: {ctx.guild_id}! Got error: {e}"
                )

            try:
                moderator_role, *none = await db.get_guild_settings(guild, settings=["moderator_role_id"])
                await ctx.rest.delete_role(guild, moderator_role)
            except hikari.ForbiddenError:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.roles_delete").error(
                    "ForbiddenError while trying to delete moderator role " f"for guild_id: {ctx.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.roles_delete").error(
                    "Unexpected error while trying to delete moderator role "
                    f"for guild_id: {ctx.guild_id}! Got error: {e}"
                )

            # DELETE CHANNELS
            try:
                channel_raids, *none = await db.get_guild_settings(guild, settings=["raids_channel_id"])
                await ctx.rest.delete_channel(channel_raids)
            except hikari.NotFoundError:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.channel_delete").error(
                    "NotFoundError while trying to delete raids channel " f"for guild_id: {ctx.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.channel_delete").error(
                    "Unexpected error while trying to delete raids channel "
                    f"for guild_id: {ctx.guild_id}! Got error: {e}"
                )

            try:
                channel_logs, *none = await db.get_guild_log_settings(guild, settings=["logs_channel_id"])
                await ctx.rest.delete_channel(channel_logs)
            except hikari.NotFoundError:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.channel_delete").error(
                    "NotFoundError while trying to delete logs channel " f"for guild_id: {ctx.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.reset.channel_delete").error(
                    "Unexpected error while trying to delete logs channel "
                    f"for guild_id: {ctx.guild_id}! Got error: {e}"
                )

            parameters = []
            parameters.append("is_setup = false")
            parameters.append("raids_channel_id = NULL")
            parameters.append("moderator_role_id = NULL")
            parameters.append("instinct_role_id = NULL")
            parameters.append("mystic_role_id = NULL")
            parameters.append("valor_role_id = NULL")
            parameters.append("instinct_emoji_id = NULL")
            parameters.append("mystic_emoji_id = NULL")
            parameters.append("valor_emoji_id = NULL")
            await db.set_guild_setting(guild, parameters=parameters)
            await db.set_guild_log_setting(guild, parameters=["logs_channel_id = NULL"])

            embed_finished = hikari.Embed(
                title=SUPPORTED_LANGUAGES.get(language).reset_finished_embed_title.format(
                    bot_name=BOT_NAME.capitalize()
                ),
                description=SUPPORTED_LANGUAGES.get(language).reset_finished_embed_description.format(
                    bot_name=BOT_NAME.capitalize()
                ),
                colour=hikari.Colour(0x8BC683),
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
                    datetime=await bot.get_timestamp_aware(gmt),
                    member=ctx.member,
                    bot_name=BOT_NAME.capitalize(),
                )
                await bot.log_from_ctx(ctx, db, log_response)
            return
