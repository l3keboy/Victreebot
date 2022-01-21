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
import tanjun
# Functionality
import asyncio
from pathlib import Path
import datetime
# Own Files
from utils import DatabaseHandler, LoggingHandler, VersionHandler
from utils.functions import get_settings
from utils.config import const

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
@component.with_slash_command
@tanjun.as_slash_command("info", "Get info about {BOT_NAME}.")
async def command_info(ctx: tanjun.abc.Context):
    try:
        lang, language, gmt, auto_delete_time, raids_channel_id, log_channel_id, moderator_role_id = await get_settings.get_all_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    version = VersionHandler.VersionHandler().version_full

    raids_channel = await ctx.rest.fetch_channel(channel=raids_channel_id)
    log_channel = await ctx.rest.fetch_channel(channel=log_channel_id)
    guild_roles = await ctx.rest.fetch_roles(guild=ctx.guild_id)
    for role in guild_roles:
        if role.id == moderator_role_id:
            moderator_role = role

    if auto_delete_time < 15:
        auto_delete_this_message = 15
    else:
        auto_delete_this_message = auto_delete_time

    embed = (
        hikari.Embed(
            title=lang.info_embed_title.format(bot_name=BOT_NAME, version=version),
            description=lang.info_embed_description.format(bot_name=BOT_NAME),
        )
            .set_footer(
            text=lang.embed_footer.format(member=ctx.member.display_name, auto_delete_time=auto_delete_this_message),
            icon=ctx.member.avatar_url,
        )
            .set_thumbnail()
            .add_field(name=lang.info_embed_lang_field_name, value=f"`{language}`", inline=False)
            .add_field(name=lang.info_embed_gmt_field_name, value=f"`{gmt}`", inline=False)
            .add_field(name=lang.info_embed_auto_delete_field_name, value=f"`{auto_delete_time} {lang.info_embed_auto_delete_field_value}`", inline=False)
            .add_field(name=lang.info_embed_raids_channel_field_name, value=f"`{raids_channel}`", inline=False)
            .add_field(name=lang.info_embed_log_channel_field_name, value=f"`{log_channel}`", inline=False)
            .add_field(name=lang.info_embed_moderator_role_field_name, value=f"`{moderator_role}`", inline=False)
            # .add_field(name="Help", value=f"The help dialog is available at `/help`\n", inline=False)
            .add_field(name="\n\u200b", value=f"\n\u200b", inline=False)
            .add_field(name=lang.info_embed_resources_field_name,
                       value=f'[{lang.info_embed_resources_field_value_1.format(bot_name=BOT_NAME)}](https://discord.com/oauth2/authorize?client_id=927258608234811394&permissions=3489917008&scope=bot%20applications.commands "{lang.info_embed_resources_field_value_2.format(bot_name=BOT_NAME)}") | '
                             f'[{lang.info_embed_resources_field_value_3}](https://www.discord.gg/ "{lang.info_embed_resources_field_value_4}")\n', inline=False)
    )

    message = await ctx.respond(embed=embed, ensure_result=True)
    await asyncio.sleep(auto_delete_this_message)
    await message.delete()

    # SEND TO LOG CHANNEL
    if log_channel_id == 'Not Configured':
        pass
    else:
        try:
            log_channel = await ctx.rest.fetch_channel(log_channel_id)
            message = await log_channel.send(lang.log_channel_info_requested.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member)) 
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_husqy.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")


# ------------------------------------------------------------------------- #
# SETTINGS GROUP COMMAND #
# ------------------------------------------------------------------------- #
settings_group = tanjun.slash_command_group("settings", f"Change settings for {BOT_NAME}.")
settings_component = tanjun.Component().add_slash_command(settings_group)


@settings_group.with_command
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD)
@tanjun.with_str_slash_option("language", "The new language of the server.", choices=[language for language in const.SUPPORTED_LANGUAGES.keys()])
@tanjun.as_slash_command("language", "Set the bots language.")
async def command_settings_language(ctx: tanjun.abc.Context, language):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    # UPDATE DATABASE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            language_to_set = "'" + language + "'"
            change_language = f'UPDATE "Settings" SET language = {language_to_set} WHERE guild_id = {ctx.guild_id}'
            await conn.fetch(change_language)
    await database.close()

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_language_changed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, language=language))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    response = lang.updated_language.format(language=language)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@settings_group.with_command
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD)
@tanjun.with_str_slash_option("offset", "The new GMT offset of the server.", choices=[offset for offset in const.SUPPORTED_TIMEZONES])
@tanjun.as_slash_command("timezone", "Set the bots timezone (GMT).")
async def command_settings_gmt(ctx: tanjun.abc.Context, offset):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    # UPDATE DATABASE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            gmt_to_set = "'" + offset + "'"
            change_gmt = f'UPDATE "Settings" SET gmt = {gmt_to_set} WHERE guild_id = {ctx.guild_id}'
            await conn.fetch(change_gmt)
    await database.close()

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_timezone_changed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, offset=offset))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    response = lang.updated_gmt.format(gmt=offset)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@settings_group.with_command
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD)
@tanjun.with_int_slash_option("seconds", "Delay in seconds.")
@tanjun.as_slash_command("auto_delete_time", "Set the delay in seconds for the bot to delete some messages.")
async def command_settings_auto_delete_time(ctx: tanjun.abc.Context, seconds):
    try:
        lang = await get_settings.get_language_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    
    # UPDATE DATABASE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            change_auto_delete_time = f'UPDATE "Settings" SET auto_delete_time = {seconds} WHERE guild_id = {ctx.guild_id}'
            await conn.fetch(change_auto_delete_time)
    await database.close()

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_auto_delete_time_changed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, seconds=seconds))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    response = lang.updated_auto_delete_time.format(seconds=seconds)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(seconds)
    await message.delete()

@settings_group.with_command
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD)
@tanjun.with_channel_slash_option("channel", "The channel to set as raids channel.")
@tanjun.as_slash_command("raids_channel", "Set the channel to which raids are posted.")
async def command_settings_raids_channel(ctx: tanjun.abc.Context, channel):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    
    # UPDATE DATABASE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            change_raids_channel = f'UPDATE "Settings" SET raids_channel = {channel.id} WHERE guild_id = {ctx.guild_id}'
            await conn.fetch(change_raids_channel)
    await database.close()
    
    # SEND TO LOG CHANNEL
    try:
        log_channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await log_channel.send(lang.log_channel_raids_channel_changed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, channel=channel))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")
        
    # SEND RESPONSE
    response = lang.updated_raids_channel_changed.format(channel=channel)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@settings_group.with_command
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD)
@tanjun.with_channel_slash_option("channel", "The channel to set as log channel. If no argument is given, the channel will be set to None.", default=None)
@tanjun.as_slash_command("log_channel", "Set the channel to which logs will be posted (including changes to raids).")
async def command_settings_log_channel(ctx: tanjun.abc.Context, channel):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    
    # UPDATE DATABASE
    if channel is None:
        change_log_channel = f'UPDATE "Settings" SET log_channel = NULL WHERE guild_id = {ctx.guild_id}'
        response = lang.updated_logs_channel_removed
        new_channel = "NULL"
    else:
        change_log_channel = f'UPDATE "Settings" SET log_channel = {channel.id} WHERE guild_id = {ctx.guild_id}'
        response = lang.updated_logs_channel_changed.format(channel=channel)
        new_channel = channel

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            await conn.fetch(change_log_channel)
    await database.close()

    # SEND TO LOG CHANNEL
    try:
        log_channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await log_channel.send(lang.log_channel_log_channel_changed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, channel=new_channel))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@settings_group.with_command
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_GUILD)
@tanjun.with_role_slash_option("role", "The role to set as moderator role.")
@tanjun.as_slash_command("moderator_role", "Set the moderator role.")
async def command_settings_moderator_role(ctx: tanjun.abc.Context, role):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    
    # UPDATE DATABASE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            change_moderator_role = f'UPDATE "Settings" SET moderator_role = {role.id} WHERE guild_id = {ctx.guild_id}'
            await conn.fetch(change_moderator_role)
    await database.close()
    new_moderator_role = role.id
    
    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_moderator_role_changed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, role=new_moderator_role))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")
        
    # SEND RESPONSE
    response = lang.updated_moderator_role_changed.format(role=new_moderator_role)
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
                await event.app.rest.delete_emoji(event.guild_id, emoji=emoji.id, reason="VictreeBot on_guild_join Handler -- Re-ïnstall")
            except hikari.ForbiddenError as e:
                LoggingHandler.LoggingHandler().logger_victreebot_join_handler.error(f"Permission error in guild: {event.guild_id}! Function: on_guild_join/emojis-delete -- Location: /commands/1_settings.py! Error: {e}")

    try:
        with open(Path("./img/emoji/instinct.png"), "rb") as image:
            instinct_image_bytes = image.read()
            instinct_emoji = await event.app.rest.create_emoji(guild=event.guild_id, name="Instinct", image=instinct_image_bytes, reason="VictreeBot on_guild_join Handler -- Install")
        with open(Path("./img/emoji/mystic.png"), "rb") as image:
            mystic_image_bytes = image.read()
            mystic_emoji = await event.app.rest.create_emoji(guild=event.guild_id, name="Mystic", image=mystic_image_bytes, reason="VictreeBot on_guild_join Handler -- Install")
        with open(Path("./img/emoji/valor.png"), "rb") as image:
            valor_image_bytes = image.read()
            valor_emoji = await event.app.rest.create_emoji(guild=event.guild_id, name="Valor", image=valor_image_bytes, reason="VictreeBot on_guild_join Handler -- Install")
    except hikari.ForbiddenError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_join_handler.error(f"Permission error in guild: {event.guild_id}! Function: on_guild_join/emojis-create -- Location: /commands/1_settings.py! Error: {e}")

    # CREATE DEFAULT ROLES
    instinct_exists = False
    mystic_exists = False
    valor_exists = False
    moderator_role_exists = False
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
        elif role.name == "VictreeBot Moderator":
            moderator_role_exists = True
            moderator_role = role
        else:
            pass

    try:
        if not instinct_exists:
            instinct_role = await event.app.rest.create_role(event.guild_id, name="Instinct", color=hikari.Colour(0xfdff00), reason="VictreeBot on_guild_join Handler -- Install")
        if not mystic_exists:
            mystic_role = await event.app.rest.create_role(event.guild_id, name="Mystic", color=hikari.Colour(0x2a6ceb), reason="VictreeBot on_guild_join Handler -- Install")
        if not valor_exists:
            valor_role = await event.app.rest.create_role(event.guild_id, name="Valor", color=hikari.Colour(0xff0000), reason="VictreeBot on_guild_join Handler -- Install")
        if not moderator_role_exists:
            moderator_role = await event.app.rest.create_role(event.guild_id, name="VictreeBot Moderator", color=hikari.Colour(0xffa500), reason="VictreeBot on_guild_join Handler -- Install")
    except hikari.ForbiddenError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_join_handler.error(f"Permission error in guild: {event.guild_id}! Function: on_guild_join/roles-create -- Location: /commands/1_settings.py! Error: {e}")

    # CREATE DEFAULT CHANNELS
    raids_channel_exists = False
    log_channel_exists = False
    all_channels = await event.app.rest.fetch_guild_channels(event.guild_id)
    for channel in all_channels:
        if channel.name == "victreebot-raids-channel":
            raids_channel = channel
            raids_channel_exists = True
        elif channel.name == "victreebot-logs-channel":
            log_channel = channel
            log_channel_exists = True
        else:
            pass

    try:
        if not raids_channel_exists:
            raids_channel = await event.app.rest.create_guild_text_channel(event.guild_id, name="victreebot-raids-channel", topic="Channel for the raids!", reason="VictreeBot on_guild_join Handler -- Install")
        if not log_channel_exists:
            log_channel = await event.app.rest.create_guild_text_channel(event.guild_id, name="victreebot-logs-channel", topic="Channel for the raids!", reason="VictreeBot on_guild_join Handler -- Install")
    except hikari.ForbiddenError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_join_handler.error(f"Permission error in guild: {event.guild_id}! Function: on_guild_join/channel-create -- Location: /commands/1_settings.py! Error: {e}")

    # ADD DEFAULTS TO DATABASE
    default_language = "en"
    default_gmt = "GMT+0"
    default_auto_delete_time = 5
    default_raids_channel = raids_channel.id
    default_log_channel = log_channel.id
    default_moderator_role = moderator_role.id

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                language_to_set = "'" + default_language + "'"
                gmt_to_set = "'" + default_gmt + "'"
                on_guild_join_query = f'INSERT INTO "Settings" (guild_id, language, gmt, auto_delete_time, raids_channel, log_channel, moderator_role) VALUES ({event.guild_id}, {language_to_set}, {gmt_to_set}, {default_auto_delete_time}, {default_raids_channel}, {default_log_channel}, {default_moderator_role})'
                await conn.fetch(on_guild_join_query)
            except asyncpg.exceptions.UniqueViolationError as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Guild_id: {event.guild_id}, already exists in Settings table!")
    await database.close()

    # CREATE GUILD TABLE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_guild_join_query_2 = f'CREATE TABLE public."{event.guild_id}" (user_id int8 NULL, friend_codes text NULL, location text NULL, stats_raids_created int4 NULL, stats_raids_participated int4 NULL, CONSTRAINT "{event.guild_id}_un" UNIQUE (user_id))'
                await conn.execute(on_guild_join_query_2)
            except asyncpg.exceptions.DuplicateTableError:
                pass
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while creating a database table for guild_id {event.guild_id}! Got error: {e}")
    await database.close()

    # ADD MEMBERS TO GUILD TABLE
    for member in event.guild.get_members():
        database = await DatabaseHandler.acquire_database()
        async with database.acquire() as conn:
            async with conn.transaction():
                try:
                    on_guild_join_query_3 = f'INSERT INTO "{event.guild_id}" (user_id, stats_raids_created, stats_raids_participated) VALUES ({member}, {0}, {0})'
                    await conn.execute(on_guild_join_query_3)
                except asyncpg.exceptions.UniqueViolationError:
                    pass
                except Exception as e:
                    LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while adding a user to guild_id {event.guild_id} database table! Got error: {e}")
        await database.close()

    # ADD SERVER TO SERVERSTATS TABLE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_guild_join_query_4 = f'INSERT INTO "ServerStats" (guild_id, stats_raids_created, stats_raids_deleted, stats_raids_completed) VALUES ({event.guild_id}, {0}, {0}, {0})'
                await conn.fetch(on_guild_join_query_4)
            except asyncpg.exceptions.UniqueViolationError as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Guild_id: {event.guild_id}, already exists in ServerStats table!")
    await database.close()

    # SEND MESSAGE
    embed = (
        hikari.Embed(
            title="Welcome to VictreeBot!",
            description="Hello! Welcome to VictreeBot! While joining this server I have done a few things for you, these can be read below! \n\n`NOTE: Please make sure that the VictreeBot role is placed ABOVE other roles!`"
        )
            .set_footer(
            text="Thanks for using VictreeBot! Encounter issues or any feature ideas? Let us now and we will have a look!",
        )
            .set_thumbnail()
            .add_field(name="Joining tasks I have completed", value=f"1) Uploaded custom emoji's.\n 2) Created roles.\n 3) Created default channels.\n The values I have used/created are listed below split in three parts (Custom emoji's, Roles and Other values)!", inline=False)
            .add_field(name="\n\u200b", value=f"\n\u200b", inline=False)
            .add_field(name="Custom Emoji's (permanent)", value=f"`name:`  Instinct\n `emoji:`  {instinct_emoji} \n `name:`  Mystic\n `emoji:`  {mystic_emoji} \n `name:`  Valor\n `emoji:`  {valor_emoji}", inline=False)
            .add_field(name="Roles (permanent)", value=f"`name:`  Instinct\n `role_id:`  {instinct_role.id} \n `name:`  Mystic\n `role_id:`  {mystic_role.id} \n `name:`  Valor\n `role_id:`  {valor_role.id}", inline=False)
            .add_field(name="Other values (changeable)", value=f"`Language:`  en \n `Timezone:`  GMT 0 \n `Auto Delete Time:`  5 \n `Raids Channel:`  {raids_channel.mention} \n `Logs Channel:`  {log_channel.mention} \n `Moderator Role:`  {moderator_role.mention} \n\n NOTE: You need the `Manage Guild` permissions to change these!", inline=False)
    )

    await log_channel.send(embed=embed)


async def on_guild_leave(event: hikari.GuildLeaveEvent):
    # REMOVE GUILD FROM SETTINGS
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_guild_remove_settings_query = f'DELETE FROM "Settings" WHERE guild_id = {event.guild_id}'
                await conn.fetch(on_guild_remove_settings_query)
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while trying to remove guild_id: {event.guild_id} from settings table!")
    await database.close()

    # REMOVE GUILD TABLE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_guild_remove_guild_table_query = f'DROP TABLE "{event.guild_id}"'
                await conn.execute(on_guild_remove_guild_table_query)
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while trying to drop guild_id {event.guild_id} table! Got error: {e}")
    await database.close()

    # REMOVE GUILD FROM SERVERSTATS
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_guild_remove_serverstats_table_query = f'DELETE FROM "ServerStats" WHERE guild_id = {event.guild_id}'
                await conn.fetch(on_guild_remove_serverstats_table_query)
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while trying to remove guild_id: {event.guild_id} from ServerStats table!")
    await database.close()

    # REMOVE GYMS OF GUILD
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_guild_remove_gym_query = f'DELETE FROM "Gym" WHERE guild_id = {event.guild_id}'
                await conn.fetch(on_guild_remove_gym_query)
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while trying to remove guild_id: {event.guild_id} from gym table!")
    await database.close()

    # REMOVE POKÉSTOPS OF GUILD
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_guild_remove_gym_query = f'DELETE FROM "Pokéstop" WHERE guild_id = {event.guild_id}'
                await conn.fetch(on_guild_remove_gym_query)
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while trying to remove guild_id: {event.guild_id} from pokéstop table!")
    await database.close()

    # REMOVE RAIDS OF GUILD
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_guild_remove_gym_query = f'DELETE FROM "Raid-Events" WHERE guild_id = {event.guild_id}'
                await conn.fetch(on_guild_remove_gym_query)
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while trying to remove guild_id: {event.guild_id} from raid-events table!")
    await database.close()


async def on_member_create(event: hikari.MemberCreateEvent):
    # ADD NEW USER TO GUILD TABLE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_member_create_query = f'INSERT INTO "{event.guild_id}" (user_id, stats_raids_created, stats_raids_participated) VALUES ({event.user_id}, {0}, {0})'
                await conn.execute(on_member_create_query)
            except asyncpg.exceptions.UniqueViolationError:
                pass
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went while trying to add a user to the servers database table for guild_id {event.guild_id}! Got error: {e}")
    await database.close()


async def on_member_delete(event: hikari.MemberDeleteEvent):
    # REMOVE USER FROM GUILD TABLE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                on_member_delete_query = f'DELETE FROM "{event.guild_id}" WHERE user_id = {event.user_id}'
                await conn.execute(on_member_delete_query)
            except asyncpg.exceptions.UniqueViolationError:
                pass
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went while trying to remove a user from the servers database table for guild_id {event.guild_id}! Got error: {e}")
    await database.close()


# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
    client.add_component(settings_component.copy())
    client.events.subscribe(hikari.GuildJoinEvent, on_guild_join)
    client.events.subscribe(hikari.GuildLeaveEvent, on_guild_leave)
    client.events.subscribe(hikari.MemberCreateEvent, on_member_create)
    client.events.subscribe(hikari.MemberDeleteEvent, on_member_delete)