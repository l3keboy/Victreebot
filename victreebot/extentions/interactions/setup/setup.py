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
@tanjun.as_slash_command("setup", f"Setup {BOT_NAME.capitalize()}")
async def command_setup(
    ctx: tanjun.abc.SlashContext,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup"]
    )

    if is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_already_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    gif = Path("../Husqy/assets/loading.gif")
    embed_started = (
        hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).setup_started_embed_title.format(bot_name=BOT_NAME.capitalize()),
            description=SUPPORTED_LANGUAGES.get(language).setup_started_embed_description.format(bot_name=BOT_NAME.capitalize()),
            colour=hikari.Colour(0x8bc683),
        )
        .set_thumbnail(gif)
    )
    response_message = await ctx.respond(embed=embed_started)

    guild = ctx.get_guild()
    my_user = await ctx.rest.fetch_my_user()

    # UPLOAD CUSTOM EMOJI'S
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

    try:
        with open(Path("./assets/emojis/instinct.png"), "rb") as image:
            instinct_image_bytes = image.read()
            instinct_emoji = await ctx.rest.create_emoji(
                guild,
                "Instinct",
                instinct_image_bytes,
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        with open(Path("./assets/emojis/mystic.png"), "rb") as image:
            mystic_image_bytes = image.read()
            mystic_emoji = await ctx.rest.create_emoji(
                guild,
                "Mystic",
                mystic_image_bytes,
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        with open(Path("./assets/emojis/valor.png"), "rb") as image:
            valor_image_bytes = image.read()
            valor_emoji = await ctx.rest.create_emoji(
                guild,
                "Valor",
                valor_image_bytes,
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").info(
            f"Added emoji's ('Instinct', 'Mystic' or 'Valor') to guild_id: {ctx.guild_id}!"
        )
    except hikari.ForbiddenError:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").error(
            "ForbiddenError while trying to add one or more emoji's ('Instinct', 'Mystic' or 'Valor') "
            f"for guild_id: {ctx.guild_id}!"
        )
    except Exception as e:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").error(
            "Unexpected error while trying to add one or more emoji's ('Instinct', 'Mystic' or 'Valor') "
            f"for guild_id: {ctx.guild_id}! Got error: {e}"
        )

    # CREATE DEFAULT ROLES
    role_instinct_exists, role_mystic_exists, role_valor_exists, role_moderator_exists = False, False, False, False
    all_server_roles = await ctx.rest.fetch_roles(guild)
    for role in all_server_roles:
        if role.name == "Instinct":
            role_instinct_exists, role_instinct = True, role
        if role.name == "Mystic":
            role_mystic_exists, role_mystic = True, role
        if role.name == "Valor":
            role_valor_exists, role_valor = True, role
        if role.name == f"{BOT_NAME.capitalize()} moderator":
            role_moderator_exists, role_moderator = True, role

    try:
        if not role_instinct_exists:
            role_instinct = await ctx.rest.create_role(
                guild,
                name="Instinct",
                color=hikari.Colour(0xFDFF00),
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        if not role_mystic_exists:
            role_mystic = await ctx.rest.create_role(
                guild,
                name="Mystic",
                color=hikari.Colour(0x2A6CEB),
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        if not role_valor_exists:
            role_valor = await ctx.rest.create_role(
                guild,
                name="Valor",
                color=hikari.Colour(0xFF0000),
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        if not role_moderator_exists:
            role_moderator = await ctx.rest.create_role(
                guild,
                name=f"{BOT_NAME.capitalize()} moderator",
                color=hikari.Colour(0xFFA500),
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_roles").info(
            "Created roles ('Instinct', 'Mystic', 'Valor' or "
            f"'{BOT_NAME.capitalize()} moderator') for guild_id: {ctx.guild_id}!"
        )
    except hikari.ForbiddenError:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_roles").error(
            "ForbiddenError while trying to create roles "
            f"('Instinct', 'Mystic', 'Valor' or '{BOT_NAME.capitalize()} moderator') "
            f"for guild_id: {ctx.guild_id}!"
        )
    except Exception as e:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_roles").error(
            f"Unexpected error while trying to create roles "
            f"('Instinct', 'Mystic', 'Valor' or '{BOT_NAME.capitalize()} moderator') "
            f"for guild_id: {ctx.guild_id}! Got error: {e}"
        )

    # CREATE DEFAULT CHANNELS
    channel_raids_exists, channel_logs_exists = False, False
    all_server_channels = await ctx.rest.fetch_guild_channels(guild)
    for channel in all_server_channels:
        if channel.name == f"{BOT_NAME.lower()}-raids":
            channel_raids_exists, channel_raids = True, channel
        if channel.name == f"{BOT_NAME.lower()}-logs":
            channel_logs_exists, channel_logs = True, channel

    try:
        if not channel_raids_exists:
            permission_overwrites = []
            permission_overwrites.append(
                hikari.PermissionOverwrite(
                    id=my_user.id,
                    type=hikari.PermissionOverwriteType.MEMBER,
                    allow=hikari.Permissions.MANAGE_CHANNELS | hikari.Permissions.SEND_MESSAGES
                )
            )
            channel_raids = await ctx.rest.create_guild_text_channel(
                guild,
                name=f"{BOT_NAME.lower()}-raids",
                permission_overwrites=permission_overwrites,
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        if not channel_logs_exists:
            permission_overwrites = []
            permission_overwrites.append(
                hikari.PermissionOverwrite(
                    id=my_user.id,
                    type=hikari.PermissionOverwriteType.MEMBER,
                    allow=hikari.Permissions.MANAGE_CHANNELS | hikari.Permissions.SEND_MESSAGES
                )
            )
            channel_logs = await ctx.rest.create_guild_text_channel(
                guild,
                name=f"{BOT_NAME.lower()}-logs",
                permission_overwrites=permission_overwrites,
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_channels").info(
            f"Created channels ('{BOT_NAME.capitalize()}-raids' and "
            f"'{BOT_NAME.capitalize()}-logs') for guild_id: {ctx.guild_id}!"
        )
    except hikari.ForbiddenError:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_channels").error(
            "ForbiddenError while trying to create channels "
            f"('{BOT_NAME.capitalize()}-raids' and '{BOT_NAME.capitalize()}-logs') "
            f"for guild_id: {ctx.guild_id}!"
        )
    except Exception as e:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_channels").error(
            "Unexpected error while trying to create channels "
            f"('{BOT_NAME.capitalize()}-raids' and '{BOT_NAME.capitalize()}-logs') "
            f"for guild_id: {ctx.guild_id}! Got error: {e}"
        )

    await db.set_guild_setting(guild, parameters=["is_setup = true", f"raids_channel_id = {channel_raids.id}"])
    await db.set_guild_log_setting(guild, parameters=[f"logs_channel_id = {channel_logs.id}"])

    # SEND MESSAGE
    embed = (
        hikari.Embed(
            title=f"Welcome to {BOT_NAME.capitalize()}!",
            description=f"Hello! Thanks for using and trusting {BOT_NAME.capitalize()}!\n"
            f"While joining the server, there are a few things that have been setup for you, these include:\n"
            f"- Created custom emoji's;\n"
            f"\u200b \u200b \u200b `Instinct`: {instinct_emoji} | `Mystic`: {mystic_emoji} | `Valor`: {valor_emoji}\n"
            f"- Created default role's;\n"
            f"\u200b \u200b \u200b `Instinct`: {role_instinct.mention} | `Mystic`: {role_mystic.mention} | `Valor`: {role_valor.mention}\n"  # noqa E501
            f"\u200b \u200b \u200b `Moderator`: {role_moderator.mention}\n"
            f"- Created default channels;\n"
            f"\u200b \u200b \u200b `Raids Channel`: {channel_raids.mention} | `Logs Channel`: {channel_logs.mention}\n\n"  # noqa E501
            f"`NOTE: Please make sure the {BOT_NAME.capitalize()} bot role is placed above all other roles to ensure the working of {BOT_NAME.capitalize()}`",  # noqa E501
            colour=hikari.Colour(0x8bc683)
        )
        .set_footer(
            text=f"Thanks for using {BOT_NAME.capitalize()}! "
            "If you encounter any issues or you have feature ideas, join our support server!",
        )
        .set_thumbnail(my_user.avatar_url)
        .add_field(
            name="Changable server settings:",
            value=f"Some default settings are changable, these include:\n"
            f"- `Language`: en\n"
            f"- `Timezone`: GMT+0\n"
            f"- `Unit Systems`: Metric System\n"
            f"- `Auto Delete`: 5 seconds\n"
            f"- `Raids Channel ID`: {channel_raids.mention}\n"
            f"- `Logs Channel ID`: {channel_logs.mention}\n\n"
            f"Make sure to change these settings to your liking to make full use of {BOT_NAME.capitalize()}!",
            inline=True,
        )
        .add_field(name="\n\u200b", value="\n\u200b", inline=False)
        .add_field(
            name=f"{BOT_NAME.capitalize()} resources:",
            value=f"[Support server]({SUPPORT_SERVER_LINK}) | [Invite {BOT_NAME.capitalize()}]({BOT_INVITE_LINK})",
            inline=False,
        )
    )
    await channel_logs.send(embed=embed)

    embed_finished = (
        hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).setup_finished_embed_title.format(bot_name=BOT_NAME.capitalize()),
            description=SUPPORTED_LANGUAGES.get(language).setup_finished_embed_description.format(bot_name=BOT_NAME.capitalize(), logs_channel_mention=channel_logs.mention),
            colour=hikari.Colour(0x8bc683),
        )
    )
    await response_message.delete()
    response_message = await ctx.rest.create_message(ctx.get_channel(), embed=embed_finished)
    await asyncio.sleep(10)
    await response_message.delete()