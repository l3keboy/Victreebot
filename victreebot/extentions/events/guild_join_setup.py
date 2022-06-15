# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import logging
import os
from pathlib import Path

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")
SUPPORT_SERVER_LINK = os.getenv("SUPPORT_SERVER_LINK")
BOT_INVITE_LINK = os.getenv("BOT_INVITE_LINK")


async def event_guild_join_setup(
    event: hikari.GuildJoinEvent,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    guild = await event.app.rest.fetch_guild(event.guild_id)
    my_user = await event.app.rest.fetch_my_user()

    # UPLOAD CUSTOM EMOJI'S
    all_server_emojis = await event.app.rest.fetch_guild_emojis(guild)
    for emoji in all_server_emojis:
        if emoji.name == "Instinct" or emoji.name == "Mystic" or emoji.name == "Valor":
            try:
                await event.app.rest.delete_emoji(
                    guild, emoji.id, reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Redo setup!"
                )
                logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").info(
                    f"Deleted emoji with same name ('Instinct', 'Mystic' or 'Valor') for guild_id: {event.guild_id}!"
                )
            except hikari.ForbiddenError:
                logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").error(
                    "ForbiddenError while trying to delete emoji with same name ('Instinct', 'Mystic' or 'Valor') "
                    f"for guild_id: {event.guild_id}!"
                )
            except Exception as e:
                logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").error(
                    "Unexpected error while trying to delete emoji with same name ('Instinct', 'Mystic' or 'Valor') "
                    f"for guild_id: {event.guild_id}! Got error: {e}"
                )

    try:
        with open(Path("./assets/emojis/instinct.png"), "rb") as image:
            instinct_image_bytes = image.read()
            instinct_emoji = await event.app.rest.create_emoji(
                guild,
                "Instinct",
                instinct_image_bytes,
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        with open(Path("./assets/emojis/mystic.png"), "rb") as image:
            mystic_image_bytes = image.read()
            mystic_emoji = await event.app.rest.create_emoji(
                guild,
                "Mystic",
                mystic_image_bytes,
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        with open(Path("./assets/emojis/valor.png"), "rb") as image:
            valor_image_bytes = image.read()
            valor_emoji = await event.app.rest.create_emoji(
                guild,
                "Valor",
                valor_image_bytes,
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").info(
            f"Added emoji's ('Instinct', 'Mystic' or 'Valor') to guild_id: {event.guild_id}!"
        )
    except hikari.ForbiddenError:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").error(
            "ForbiddenError while trying to add one or more emoji's ('Instinct', 'Mystic' or 'Valor') "
            f"for guild_id: {event.guild_id}!"
        )
    except Exception as e:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.emojis_upload").error(
            "Unexpected error while trying to add one or more emoji's ('Instinct', 'Mystic' or 'Valor') "
            f"for guild_id: {event.guild_id}! Got error: {e}"
        )

    # CREATE DEFAULT ROLES
    role_instinct_exists, role_mystic_exists, role_valor_exists, role_moderator_exists = False, False, False, False
    all_server_roles = await event.app.rest.fetch_roles(guild)
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
            role_instinct = await event.app.rest.create_role(
                guild,
                name="Instinct",
                color=hikari.Colour(0xFDFF00),
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        if not role_mystic_exists:
            role_mystic = await event.app.rest.create_role(
                guild,
                name="Mystic",
                color=hikari.Colour(0x2A6CEB),
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        if not role_valor_exists:
            role_valor = await event.app.rest.create_role(
                guild,
                name="Valor",
                color=hikari.Colour(0xFF0000),
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        if not role_moderator_exists:
            role_moderator = await event.app.rest.create_role(
                guild,
                name=f"{BOT_NAME.capitalize()} moderator",
                color=hikari.Colour(0xFFA500),
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_roles").info(
            "Created roles ('Instinct', 'Mystic', 'Valor' or "
            f"'{BOT_NAME.capitalize()} moderator') for guild_id: {event.guild_id}!"
        )
    except hikari.ForbiddenError:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_roles").error(
            "ForbiddenError while trying to create roles "
            f"('Instinct', 'Mystic', 'Valor' or '{BOT_NAME.capitalize()} moderator') "
            f"for guild_id: {event.guild_id}!"
        )
    except Exception as e:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_roles").error(
            f"Unexpected error while trying to create roles "
            f"('Instinct', 'Mystic', 'Valor' or '{BOT_NAME.capitalize()} moderator') "
            f"for guild_id: {event.guild_id}! Got error: {e}"
        )

    # CREATE DEFAULT CHANNELS
    channel_raids_exists, channel_logs_exists = False, False
    all_server_channels = await event.app.rest.fetch_guild_channels(guild)
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
                    allow=hikari.Permissions.MANAGE_CHANNELS | hikari.Permissions.SEND_MESSAGES | hikari.Permissions.VIEW_CHANNEL
                )
            )
            channel_raids = await event.app.rest.create_guild_text_channel(
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
                    allow=hikari.Permissions.MANAGE_CHANNELS | hikari.Permissions.SEND_MESSAGES | hikari.Permissions.VIEW_CHANNEL
                )
            )
            channel_logs = await event.app.rest.create_guild_text_channel(
                guild,
                name=f"{BOT_NAME.lower()}-logs",
                permission_overwrites=permission_overwrites,
                reason=f"{BOT_NAME.capitalize()} event_guild_join_setup Handler -- Setup!",
            )
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_channels").info(
            f"Created channels ('{BOT_NAME.capitalize()}-raids' and "
            f"'{BOT_NAME.capitalize()}-logs') for guild_id: {event.guild_id}!"
        )
    except hikari.ForbiddenError:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_channels").error(
            "ForbiddenError while trying to create channels "
            f"('{BOT_NAME.capitalize()}-raids' and '{BOT_NAME.capitalize()}-logs') "
            f"for guild_id: {event.guild_id}!"
        )
    except Exception as e:
        logging.getLogger(f"{BOT_NAME.lower()}.events.event_guild_join_setup.create_channels").error(
            "Unexpected error while trying to create channels "
            f"('{BOT_NAME.capitalize()}-raids' and '{BOT_NAME.capitalize()}-logs') "
            f"for guild_id: {event.guild_id}! Got error: {e}"
        )

    # ADD SERVER TO DATABASE
    await db.insert_guild(guild)
    await db.insert_guild_settings(guild, channel_raids)
    await db.insert_guild_log_settings(guild, channel_logs)

    # ADD USERS TO DATABASE
    all_server_members = await event.app.rest.fetch_members(guild)
    for member in all_server_members:
        await db.insert_user(guild, member)

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
