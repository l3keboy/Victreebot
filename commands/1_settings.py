# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #
# IMPORTS
# Database and .env
import os
import asyncpg
from dotenv import load_dotenv
# Hikari
import hikari
from hikari.events import voice_events
from hikari.traits import ExecutorAware
import tanjun
# Functionality
import asyncio
from pathlib import Path

from tanjun.conversion import EmojiConverter
# Own Files
from utils import DatabaseHandler
from utils.LoggingHandler import LoggingHandler
from utils.functions import get_settings

# .ENV AND .ENV VARIABLES
# Load .env
load_dotenv()
# Variables
# Bot Variables
BOT_NAME = os.getenv("BOT_NAME")

component = tanjun.Component()

# ------------------------------------------------------------------------- #
# SLASH COMMANDS #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# SETTINGS GROUP COMMAND #
# ------------------------------------------------------------------------- #
settings_group = tanjun.slash_command_group("settings", f"Change settings for {BOT_NAME}.")
settings_component = tanjun.Component().add_slash_command(settings_group)

@settings_group.with_command
@tanjun.with_str_slash_option("language", "The new language of the server.", choices=["en"])
@tanjun.as_slash_command("language", "Set the bots language.")
async def command_settings_language(ctx: tanjun.abc.Context, language):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            language_to_set = "'" + language + "'"
            change_language = f'UPDATE "Settings" SET language = {language_to_set} WHERE guild_id = {ctx.guild_id}'
            await conn.fetch(change_language)
    await database.close()

    response = lang.updated_language.format(language=language)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@settings_group.with_command
@tanjun.with_str_slash_option("offset", "The new GMT offset of the server.", choices=["GMT -12","GMT -11","GMT -10","GMT -9","GMT -8","GMT -7","GMT -6","GMT -5","GMT -4","GMT -3","GMT -2","GMT -1","GMT 0", "GMT +1","GMT +2","GMT +3","GMT +4","GMT +5","GMT +6","GMT +7","GMT +8","GMT +9","GMT +10","GMT +11","GMT +12"])
@tanjun.as_slash_command("timezone", "Set the bots timezone (GMT).")
async def command_settings_gmt(ctx: tanjun.abc.Context, offset):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            gmt_to_set = "'" + offset + "'"
            change_gmt = f'UPDATE "Settings" SET gmt = {gmt_to_set} WHERE guild_id = {ctx.guild_id}'
            await conn.fetch(change_gmt)
    await database.close()

    response = lang.updated_gmt.format(gmt=offset)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@settings_group.with_command
@tanjun.with_int_slash_option("seconds", "Delay in seconds.")
@tanjun.as_slash_command("auto_delete_time", "Set the delay in seconds for the bot to delete some messages.")
async def command_settings_auto_delete_time(ctx: tanjun.abc.Context, seconds):
    try:
        lang = await get_settings.get_language_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            change_auto_delete_time = f'UPDATE "Settings" SET auto_delete_time = {seconds} WHERE guild_id = {ctx.guild_id}'
            await conn.fetch(change_auto_delete_time)
    await database.close()

    response = lang.updated_auto_delete_time.format(seconds=seconds)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(seconds)
    await message.delete()

@settings_group.with_command
@tanjun.with_channel_slash_option("channel", "The channel to set as raids channel. If no argument is given, the channel will be set to None", default=None)
@tanjun.as_slash_command("raids_channel", "Set the channel to which raids are posted.")
async def command_settings_raids_channel(ctx: tanjun.abc.Context, channel):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    
    if channel is None:
        change_raids_channel = f'UPDATE "Settings" SET raids_channel = NULL WHERE guild_id = {ctx.guild_id}'
        response = lang.updated_raids_channel_removed
    else:
        change_raids_channel = f'UPDATE "Settings" SET raids_channel = {channel.id} WHERE guild_id = {ctx.guild_id}'
        response = lang.updated_raids_channel_changed.format(channel=channel)

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            await conn.fetch(change_raids_channel)
    await database.close()

    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@settings_group.with_command
@tanjun.with_channel_slash_option("channel", "The channel to set as log channel. If no argument is given, the channel will be set to None", default=None)
@tanjun.as_slash_command("log_channel", "Set the channel to which logs will be posted (including changes to raids).")
async def command_settings_log_channel(ctx: tanjun.abc.Context, channel):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    
    if channel is None:
        change_log_channel = f'UPDATE "Settings" SET log_channel = NULL WHERE guild_id = {ctx.guild_id}'
        response = lang.updated_logs_channel_removed
    else:
        change_log_channel = f'UPDATE "Settings" SET log_channel = {channel.id} WHERE guild_id = {ctx.guild_id}'
        response = lang.updated_logs_channel_changed.format(channel=channel)

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            await conn.fetch(change_log_channel)
    await database.close()

    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()


# ------------------------------------------------------------------------- #
# EVENT LISTENERS #
# ------------------------------------------------------------------------- #
async def on_guild_join(event: hikari.GuildJoinEvent):
    # UPLOAD CUSTOM EMOJI'S
    all_server_emojis = await event.app.rest.fetch_guild_emojis(event.guild_id)
    for emoji in all_server_emojis:
        if emoji.name == "Instinct" or emoji.name == "Mystic" or emoji.name == "Valor":
            try:
                await event.app.rest.delete_emoji(event.guild_id, emoji=emoji.id, reason="Victree on_guild_join Handler -- Re-ïnstall")
            except hikari.ForbiddenError as e:
                LoggingHandler().logger_victreebot_join_handler.error(f"Permission error in guild: {event.guild_id}! Function: on_guild_join/emojis-delete -- Location: /commands/1_settings.py! Error: {e}")

    try:
        with open(Path("./img/emoji/instinct.png"), "rb") as image:
            instinct_image_bytes = image.read()
            instinct_emoji = await event.app.rest.create_emoji(guild=event.guild_id, name="Instinct", image=instinct_image_bytes, reason="Victree on_guild_join Handler -- Install")
        with open(Path("./img/emoji/mystic.png"), "rb") as image:
            mystic_image_bytes = image.read()
            mystic_emoji = await event.app.rest.create_emoji(guild=event.guild_id, name="Mystic", image=mystic_image_bytes, reason="Victree on_guild_join Handler -- Install")
        with open(Path("./img/emoji/valor.png"), "rb") as image:
            valor_image_bytes = image.read()
            valor_emoji = await event.app.rest.create_emoji(guild=event.guild_id, name="Valor", image=valor_image_bytes, reason="Victree on_guild_join Handler -- Install")
    except hikari.ForbiddenError as e:
        LoggingHandler().logger_victreebot_join_handler.error(f"Permission error in guild: {event.guild_id}! Function: on_guild_join/emojis-create -- Location: /commands/1_settings.py! Error: {e}")

    # CREATE DEFAULT ROLES
    instinct_exists = False
    mystic_exists = False
    valor_exists = False
    all_roles = await event.app.rest.fetch_roles(event.guild_id)
    for role in all_roles:
        if role.name == "Instinct":
            instinct_exists = True
            instinct_role = role
        elif role.name == "Mystic":
            mystic_exists = True
            mystic_role = role
        elif role.name == "Valor":
            valor_exists = True
            valor_role = role
        else:
            pass

    try:
        if not instinct_exists:
            instinct_role = await event.app.rest.create_role(event.guild_id, name="Instinct", color=hikari.Colour(0xfdff00), reason="Victree on_guild_join Handler -- Install")
        if not mystic_exists:
            mystic_role = await event.app.rest.create_role(event.guild_id, name="Mystic", color=hikari.Colour(0x2a6ceb), reason="Victree on_guild_join Handler -- Install")
        if not valor_exists:
            valor_role = await event.app.rest.create_role(event.guild_id, name="Valor", color=hikari.Colour(0xff0000), reason="Victree on_guild_join Handler -- Install")
    except hikari.ForbiddenError as e:
        LoggingHandler().logger_victreebot_join_handler.error(f"Permission error in guild: {event.guild_id}! Function: on_guild_join/roles-create -- Location: /commands/1_settings.py! Error: {e}")

    # CREATE DEFAULT CHANNELS
    raids_channel_exists = False
    log_channel_exists = False
    all_channels = await event.app.rest.fetch_guild_channels(event.guild_id)
    for channel in all_channels:
        if channel.name == "victree-raids-channel":
            raids_channel = channel
            raids_channel_exists = True
        elif channel.name == "victree-logs-channel":
            log_channel = channel
            log_channel_exists = True
        else:
            pass

    try:
        if not raids_channel_exists:
            raids_channel = await event.app.rest.create_guild_text_channel(event.guild_id, name="victree-raids-channel", topic="Channel for the raids!", reason="Victree on_guild_join Handler -- Install")
        if not log_channel_exists:
            log_channel = await event.app.rest.create_guild_text_channel(event.guild_id, name="victree-logs-channel", topic="Channel for the raids!", reason="Victree on_guild_join Handler -- Install")
    except hikari.ForbiddenError as e:
        LoggingHandler().logger_victreebot_join_handler.error(f"Permission error in guild: {event.guild_id}! Function: on_guild_join/channel-create -- Location: /commands/1_settings.py! Error: {e}")

    # ADD DEFAULTS TO DATABASE
    default_language = "en"
    default_gmt = "GMT 0"
    default_auto_delete_time = 5
    default_raids_channel = raids_channel.id
    default_log_channel = log_channel.id

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                language_to_set = "'" + default_language + "'"
                gmt_to_set = "'" + default_gmt + "'"
                on_guild_join_query = f'INSERT INTO "Settings" (guild_id, language, gmt, auto_delete_time, raids_channel, log_channel) VALUES ({event.guild_id}, {language_to_set}, {gmt_to_set}, {default_auto_delete_time}, {default_raids_channel}, {default_log_channel})'
                await conn.fetch(on_guild_join_query)
            except asyncpg.exceptions.UniqueViolationError as e:
                LoggingHandler().logger_victreebot_database.error(f"Guild_id: {event.guild_id}, already exists in Settings table!")
    await database.close()

    embed = (
        hikari.Embed(
            title="Welcome to Victree!",
            description="Hello! Welcome to Victree! While joining this server I have done a few things for you, these can be read below! \n\n`NOTE: Please make sure that the VictreeBot role is placed ABOVE other roles!`"
        )
            .set_footer(
            text="NOTE: Please make sure that the VictreeBot role is placed ABOVE other roles!",
        )
            .set_thumbnail()
            .add_field(name="Joining tasks I have completed", value=f"1) Uploaded custom emoji's.\n 2) Created roles.\n 3) Created default channels.\n The values I have used/created are listed below split in three parts (Custom emoji's, Roles and Other values)!", inline=False)
            .add_field(name="\n\u200b", value=f"\n\u200b", inline=False)
            .add_field(name="Custom Emoji's (permanent)", value=f"`name:`  Instinct\n `emoji:`  {instinct_emoji} \n `name:`  Mystic\n `emoji:`  {mystic_emoji} \n `name:`  Valor\n `emoji:`  {valor_emoji}", inline=False)
            .add_field(name="Roles (permanent)", value=f"`name:`  Instinct\n `role_id:`  {instinct_role.id} \n `name:`  Mystic\n `role_id:`  {mystic_role.id} \n `name:`  Valor\n `role_id:`  {valor_role.id}", inline=False)
            .add_field(name="Other values (changeable)", value=f"`Language:`  en \n `Timezone:`  GMT 0 \n `Auto Delete Time:`  5 \n `Raids Channel:`  {raids_channel.mention} \n `Logs Channel:`  {log_channel.mention}", inline=False)
            .add_field(name="\n\u200b", value=f"\n\u200b", inline=False)
    )

    await log_channel.send(embed=embed)


# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
    client.add_component(settings_component.copy())
    client.events.subscribe(hikari.GuildJoinEvent, on_guild_join)