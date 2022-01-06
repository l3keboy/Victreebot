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
import re
from typing import Text
import asyncpg
from dotenv import load_dotenv
# Hikari
import hikari
from hikari.traits import ExecutorAware
import tanjun
# Functionality
import asyncio
import uuid
import datetime
import pytz
# Own Files
from utils import DatabaseHandler, LoggingHandler
from utils.functions import get_raid, get_settings, pokemon, validate

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
# RAID GROUP COMMAND #
# ------------------------------------------------------------------------- #
raid_group = tanjun.slash_command_group("raid", f"Create/Delete/Get info about a raid.")
raid_component = tanjun.Component().add_slash_command(raid_group)

@raid_group.with_command
@tanjun.with_str_slash_option("date", "The date the raid take place. MUST BE IN FORMAT: DD-MM-YYYY", default="Current date in your timezone")
@tanjun.with_str_slash_option("time", "The time of the raid (f.e. 12:00). MUST BE IN FORMAT: HH:MM!")
@tanjun.with_str_slash_option("location", "The location of the raid.")
@tanjun.with_str_slash_option("boss", "The boss to fight.")
@tanjun.with_str_slash_option("raid_type", "The type of the raid.", choices=["Raid", "Mega-Raid", "EX-Raid"])
@tanjun.as_slash_command("create", "Create a raid.")
async def command_raid_create(ctx: tanjun.abc.Context, raid_type, boss, location, time, date):
    try:
        lang, gmt, auto_delete_time = await get_settings.get_language_gmt_auto_delete_time_settings(guild_id=ctx.guild_id)
        raids_channel_id, log_channel_id = await get_settings.get_channels_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    # GENERATE ID
    raid_id = str(uuid.uuid4())[:8]

    # GET TIMESTAMP IN SERVERS TIMEZONE
    timezone = pytz.timezone(f"Etc/{gmt}")
    timestamp = datetime.datetime.now(timezone).strftime("%d-%m-%Y %H:%M")

    # VALIDATE LOCATION
    location_exists, latitude, longitude = await validate.__validate_location(guild_id=ctx.guild_id, location=location)
    if not location_exists:
        response = lang.raid_location_does_not_exist.format(name=location.lower())
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return
    
    # VALIDATE TIME
    time_is_valid = await validate.__validate_time(time=time)
    if not time_is_valid:
        response = lang.raid_invalid_time_format
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    # VALIDATE DATE
    if date == "Current date in your timezone":
        date = datetime.datetime.now().strftime('%d-%m-%Y')
    else:
        date_is_valid = await validate.__validate_date(date=date)
        if not date_is_valid:
            response = lang.raid_invalid_date_format
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
        
    # VALIDATE BOSS
    success, poke_img = await pokemon.get_pokemon_img(boss=boss)
    if not success:
        response = lang.pokemon_not_found.format(pokemon=boss.lower())
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return
    
    # SEND EMBED TO RAID CHANNEL
    emojis = await ctx.rest.fetch_guild_emojis(ctx.guild_id)
    emoji_list = []
    for emoji in emojis:
        if emoji.name == "Instinct" or emoji.name == "Mystic" or emoji.name == "Valor":
            emoji_list.append(emoji)
    emoji_list.append("🇷")
    emoji_list.append("1️⃣")
    emoji_list.append("2️⃣")
    emoji_list.append("3️⃣")
            
    embed = (
        hikari.Embed(
            description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{time} - {gmt}", date=date, location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
        )
            .set_author(name=boss, icon=poke_img)
            .set_footer(
            text=lang.raid_embed_footer.format(member=ctx.member.display_name, attendees="0"),
        )
            .set_thumbnail(poke_img)
            .add_field(name="Instinct:", value="\u200b", inline=False)
            .add_field(name="Mystic:", value="\u200b", inline=False)
            .add_field(name="Valor:", value="\u200b", inline=False)
            .add_field(name="Remote:", value="\u200b", inline=False)
    )

    try:
        channel = await ctx.rest.fetch_channel(channel=raids_channel_id)
        raid_message = await channel.send(embed=embed)
        for emoji in emoji_list:
            await raid_message.add_reaction(emoji)
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send raid embed for guild_id: {ctx.guild_id}! Got error: {e}")

    # ADD RAID TO DATABASE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                id_to_set = "'" + str(raid_id) + "'" 
                timestamp_to_set = "'" + str(timestamp) + "'"
                type_to_set = "'" + raid_type + "'"
                boss_to_set = "'" + boss + "'"
                location_to_set = "'" + location + "'"
                time_to_set = "'" + time + "'"
                date_to_set = "'" + date + "'"
                add_raid = f'INSERT INTO "Raid-Events" (id, created_at, type, guild_id, channel_id, message_id, user_id, boss, location, time, date, instinct_present, mystic_present, valor_present, remote_present, total_attendees) VALUES ({id_to_set}, {timestamp_to_set}, {type_to_set}, {ctx.guild_id}, {raid_message.channel_id}, {raid_message.id}, {ctx.member.id}, {boss_to_set}, {location_to_set}, {time_to_set}, {date_to_set}, NULL, NULL, NULL, NULL, {0})'
                await conn.fetch(add_raid)
                database_success = True
            except asyncpg.exceptions.UniqueViolationError:
                database_success = False
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while trying to insert a new raid. ID already exists!")
    await database.close()

    if not database_success:
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_raid_creation_failed.format(datetime=datetime.datetime.now().strftime('%d-/%m-%Y %H:%M:%S'), member=ctx.member, raid_type=raid_type))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

        response = lang.raid_generated_id_duplicate
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    # SEND CREATE MESSAGE TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_raid_successfully_created.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, raid_type=raid_type))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    response = lang.raid_successfully_created.format(raid_type=raid_type)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

    await asyncio.sleep(7200)
    try:
        await raid_message.delete()
    except hikari.NotFoundError:
        pass

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            id_to_delete = "'" + str(raid_id) + "'" 
            delete_raid = f'DELETE FROM "Raid-Events" WHERE id = {id_to_delete} AND guild_id = {ctx.guild_id}'
            await conn.fetch(delete_raid)
    await database.close()

@raid_group.with_command
@tanjun.with_str_slash_option("raid_id", "The ID of the raid to delete")
@tanjun.with_str_slash_option("raid_type", "The type of the raid to delete.", choices=["Raid", "Mega-Raid", "EX-Raid"])
@tanjun.as_slash_command("delete", "Delete a raid.")
async def command_raid_delete(ctx: tanjun.abc.Context, raid_type, raid_id):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        raids_channel_id, log_channel_id = await get_settings.get_channels_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    # GET DETAILS OF RAID TO DELETE
    success, raid_id, created_at, raid_type, guild_id, channel_id, message_id, user_id, boss, location, time, date, instinct_present, mystic_present, valor_present, remote_present, total_attendees = await get_raid.get_raid_by_raidid_raidtype(search_raid_type=raid_type, search_raid_id=raid_id)
    if not success:
        response = lang.raid_unable_to_find.format(id=raid_id)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    # DELETE FROM DATABASE
    if not ctx.member.id == user_id:
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_raid_deletion_failed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, raid_type=raid_type))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

        response = lang.raid_unable_to_delete_not_creator
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            id_to_delete = "'" + str(raid_id) + "'" 
            delete_raid = f'DELETE FROM "Raid-Events" WHERE id = {id_to_delete} AND guild_id = {ctx.guild_id} AND user_id = {ctx.member.id}'
            await conn.fetch(delete_raid)
    await database.close()

    # SEND DELETE MESSAGE TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_raid_successfully_deleted.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, raid_type=raid_type, id=raid_id))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # DELETE CORRESPONDING MESSAGE
    try:
        raid_message_to_delete = await ctx.rest.fetch_message(channel=channel_id, message=message_id)
        await raid_message_to_delete.delete()
    except hikari.NotFoundError:
        pass

    # SEND RESPONSE
    response = lang.raid_successfully_deleted.format(id=raid_id)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()

@raid_group.with_command
@tanjun.with_str_slash_option("new_date", "New date. If no arguments are given, the date will not change!", default=None)
@tanjun.with_str_slash_option("new_time", "New time. If no arguments are given, the time will not change!", default=None)
@tanjun.with_str_slash_option("new_location", "New location. If no arguments are given, the location will not change!", default=None)
@tanjun.with_str_slash_option("new_boss", "New boss. If no arguments are given, the boss will not change!", default=None)
@tanjun.with_str_slash_option("new_type", "New type. If no arguments are given, the type will not change!", default=None, choices=["Raid", "Mega-Raid", "EX-Raid"])
@tanjun.with_str_slash_option("raid_id", "The ID of the raid to edit")
@tanjun.with_str_slash_option("raid_type", "The type of the raid to edit.", choices=["Raid", "Mega-Raid", "EX-Raid"])
@tanjun.as_slash_command("edit", "Edit a raid.")
async def command_raid_edit(ctx: tanjun.abc.Context, raid_type, raid_id, new_type, new_boss, new_location, new_time, new_date):
    try:
        lang, gmt, auto_delete_time = await get_settings.get_language_gmt_auto_delete_time_settings(guild_id=ctx.guild_id)
        raids_channel_id, log_channel_id = await get_settings.get_channels_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
        
    # GET DETAILS OF RAID TO EDIT
    success, raid_id, created_at, raid_type, guild_id, channel_id, message_id, user_id, boss, location, time, date, instinct_present, mystic_present, valor_present, remote_present, total_attendees = await get_raid.get_raid_by_raidid_raidtype(search_raid_type=raid_type, search_raid_id=raid_id)
    if not success:
        response = lang.raid_unable_to_find.format(id=raid_id)
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    parameters = []
    if not ctx.member.id == user_id:
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_raid_edit_failed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, raid_type=raid_type))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

        response = lang.raid_unable_to_edit_not_creator
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    # HANDLE NEW TYPE
    if new_type is not None:
        type_to_set = "'" + new_type + "'"
        new_type_parameter = f'"type" = {type_to_set}'
        parameters.append(new_type_parameter)
        raid_type = new_type

    # VALIDATE BOSS
    success, poke_img = await pokemon.get_pokemon_img(boss=boss)
    if not success:
        response = lang.pokemon_not_found.format(pokemon=boss.lower())
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
        return

    if new_boss is not None:
        success, poke_img = await pokemon.get_pokemon_img(boss=new_boss)
        if not success:
            response = lang.pokemon_not_found.format(pokemon=new_boss.lower())
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return

        boss_to_set = "'" + new_boss.lower() + "'"
        new_boss_parameter = f'"boss" = {boss_to_set}'
        parameters.append(new_boss_parameter)
        boss = new_boss.lower()

    # HANDLE NEW LOCATION
    location_exists, latitude, longitude = await validate.__validate_location(guild_id=ctx.guild_id, location=location)
    if new_location is not None:
        location_exists, latitude, longitude = await validate.__validate_location(guild_id=ctx.guild_id, location=new_location)
        if not location_exists:
            response = lang.raid_location_does_not_exist.format(name=new_location.lower())
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return

        location_to_set = "'" + new_location + "'"
        new_location_parameter = f'"location" = {location_to_set}'
        parameters.append(new_location_parameter)
        location = new_location
        latitude = latitude
        longitude = longitude

    # HANDLE NEW TIME
    if new_time is not None:
        time_is_valid = await validate.__validate_time(time=new_time)
        if not time_is_valid:
            response = lang.raid_invalid_time_format
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
        time_to_set = "'" + new_time + "'"
        new_time_parameter = f'"time" = {time_to_set}'
        parameters.append(new_time_parameter)
        time = new_time

    # HANDLE NEW DATE
    if new_date is not None: 
        date_is_valid = await validate.__validate_date(date=new_date)
        if not date_is_valid:
            response = lang.raid_invalid_date_format
            message = await ctx.respond(response, ensure_result=True)
            await asyncio.sleep(auto_delete_time)
            await message.delete()
            return
        date_to_set = "'" + new_date + "'"
        new_date_parameter = f'"date" = {date_to_set}'
        parameters.append(new_date_parameter)
        date = new_date

    # UPDATE DATABASE
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            id_to_change = "'" + raid_id + "'"
            update_raid = f'UPDATE "Raid-Events" SET {",".join(change for change in parameters)} WHERE guild_id = {ctx.guild_id} AND id = {id_to_change}'
            await conn.fetch(update_raid)
    await database.close()

    # EDIT MESSAGE
    embed = (
        hikari.Embed(
            description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
        )
            .set_author(name=boss, icon=poke_img)
            .set_footer(
            text=lang.raid_embed_footer.format(member=ctx.member.display_name, attendees=total_attendees),
        )
            .set_thumbnail(poke_img)
            .add_field(name="Instinct:", value=",".join(user for user in instinct_present), inline=False)
            .add_field(name="Mystic:", value=",".join(user for user in mystic_present), inline=False)
            .add_field(name="Valor:", value=",".join(user for user in valor_present), inline=False)
            .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
    )
    
    try:
        raid_message_to_edit = await ctx.rest.fetch_message(channel=channel_id, message=message_id)
        await raid_message_to_edit.edit(embed=embed)
    except hikari.NotFoundError:
        pass
    
    # SEND RESPONSE
    response = lang.raid_successfully_edited.format(id=raid_id)
    message = await ctx.respond(response, ensure_result=True)
    await asyncio.sleep(auto_delete_time)
    await message.delete()
    
    # SEND EDIT MESSAGE TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_raid_successfully_edited.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, raid_type=raid_type, id=raid_id))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

# ------------------------------------------------------------------------- #
# EVENT LISTENERS #
# ------------------------------------------------------------------------- #
async def on_guild_reaction_add(event: hikari.GuildReactionAddEvent):
    try:
        lang, gmt, auto_delete_time = await get_settings.get_language_gmt_auto_delete_time_settings(guild_id=event.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    if event.member.is_bot:
        pass
    else:
        success, raid_id, created_at, raid_type, guild_id, channel_id, message_id, user_id, boss, location, time, date, instinct_present, mystic_present, valor_present, remote_present, total_attendees = await get_raid.get_raid_by_guild_channel_message(guild_id=event.guild_id, channel_id=event.channel_id, message_id=event.message_id)
        if not success:
            return

        if total_attendees is None:
            total_attendees = 0

        if event.emoji_name == "Instinct":
            if instinct_present is None:
                new_instinct_present = [event.member.display_name]
            else: 
                instinct_present_list = instinct_present.split(",")
                try:
                    instinct_present_list.remove("\u200b")
                except Exception as e:
                    pass
                instinct_present_list.append(event.member.display_name)
                new_instinct_present = instinct_present_list
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = remote_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees + 1
                    instinct_present_to_set = "'" + ", ".join(user for user in new_instinct_present) + "'"
                    update_raid = f'UPDATE "Raid-Events" SET instinct_present = {instinct_present_to_set}, total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=event.member.display_name, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in new_instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "Mystic":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                new_mystic_present = [event.member.display_name]
            else: 
                mystic_present_list = mystic_present.split(",")
                try:
                    mystic_present_list.remove("\u200b")
                except Exception as e:
                    pass
                mystic_present_list.append(event.member.display_name)
                new_mystic_present = mystic_present_list
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = remote_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees + 1
                    mystic_present_to_set = "'" + ", ".join(user for user in new_mystic_present) + "'"
                    update_raid = f'UPDATE "Raid-Events" SET mystic_present = {mystic_present_to_set}, total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=event.member.display_name, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in new_mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "Valor":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                new_valor_present = [event.member.display_name]
            else: 
                valor_present_list = valor_present.split(",")
                try:
                    valor_present_list.remove("\u200b")
                except Exception as e:
                    pass
                valor_present_list.append(event.member.display_name)
                new_valor_present = valor_present_list
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = remote_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees + 1
                    valor_present_to_set = "'" + ",".join(user for user in new_valor_present) + "'"
                    update_raid = f'UPDATE "Raid-Events" SET valor_present = {valor_present_to_set}, total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=event.member.display_name, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in new_valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "🇷":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                new_remote_present = [event.member.display_name]
            else: 
                remote_present_list = remote_present.split(",")
                try:
                    remote_present_list.remove("\u200b")
                except Exception as e:
                    pass
                remote_present_list.append(event.member.display_name)
                new_remote_present = remote_present_list
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees + 1
                    remote_present_to_set = "'" + ",".join(user for user in new_remote_present) + "'"
                    update_raid = f'UPDATE "Raid-Events" SET remote_present = {remote_present_to_set}, total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=event.member.display_name, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in new_remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass
            
        if event.emoji_name == "1️⃣":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = valor_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees + 1
                    update_raid = f'UPDATE "Raid-Events" SET total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=event.member.display_name, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "2️⃣":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = valor_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees + 2
                    update_raid = f'UPDATE "Raid-Events" SET total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=event.member.display_name, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "3️⃣":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = valor_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees + 3
                    update_raid = f'UPDATE "Raid-Events" SET total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=event.member.display_name, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass


async def on_guild_reaction_delete(event: hikari.GuildReactionDeleteEvent):
    try:
        lang, gmt, auto_delete_time = await get_settings.get_language_gmt_auto_delete_time_settings(guild_id=event.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return
    member = await event.app.rest.fetch_user(event.user_id)
    if member.is_bot:
        pass
    else:
        success, raid_id, created_at, raid_type, guild_id, channel_id, message_id, user_id, boss, location, time, date, instinct_present, mystic_present, valor_present, remote_present, total_attendees = await get_raid.get_raid_by_guild_channel_message(guild_id=event.guild_id, channel_id=event.channel_id, message_id=event.message_id)
        if not success:
            return

        raid_owner = await event.app.rest.fetch_user(user_id)
        if event.emoji_name == "Instinct":
            if instinct_present is None:
                new_instinct_present = "\u200b"
            else: 
                instinct_present_list = instinct_present.split(",")
                instinct_present_list.remove(member.username)
                if instinct_present_list == []:
                    new_instinct_present = "\u200b"
                else:
                    new_instinct_present = instinct_present_list
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = remote_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees - 1
                    instinct_present_to_set = "'" + ",".join(user for user in new_instinct_present) + "'"
                    update_raid = f'UPDATE "Raid-Events" SET instinct_present = {instinct_present_to_set}, total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=raid_owner.username, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in new_instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=", ".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "Mystic":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                new_mystic_present = "\u200b"
            else: 
                mystic_present_list = mystic_present.split(",")
                mystic_present_list.remove(member.username)
                if mystic_present_list == []:
                    new_mystic_present = "\u200b"
                else:
                    new_mystic_present = mystic_present_list
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = remote_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees - 1
                    mystic_present_to_set = "'" + ",".join(user for user in new_mystic_present) + "'"
                    update_raid = f'UPDATE "Raid-Events" SET mystic_present = {mystic_present_to_set}, total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=raid_owner.username, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in new_mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=", ".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "Valor":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                new_valor_present = "\u200b"
            else: 
                valor_present_list = valor_present.split(",")
                valor_present_list.remove(member.username)
                if valor_present_list == []:
                    new_valor_present = "\u200b"
                else:
                    new_valor_present = valor_present_list
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = remote_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees - 1
                    valor_present_to_set = "'" + ",".join(user for user in new_valor_present) + "'"
                    update_raid = f'UPDATE "Raid-Events" SET valor_present = {valor_present_to_set}, total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=raid_owner.username, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in new_valor_present), inline=False)
                    .add_field(name="Remote:", value=", ".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "🇷":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                new_remote_present = "\u200b"
            else: 
                remote_present_list = remote_present.split(",")
                remote_present_list.remove(member.username)
                if remote_present_list == []:
                    new_remote_present = "\u200b"
                else:
                    new_remote_present = remote_present_list

            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees - 1
                    remote_present_to_set = "'" + ",".join(user for user in new_remote_present) + "'"
                    update_raid = f'UPDATE "Raid-Events" SET remote_present = {remote_present_to_set}, total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=raid_owner.username, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=", ".join(user for user in new_remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "1️⃣":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = valor_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees - 1
                    update_raid = f'UPDATE "Raid-Events" SET total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=raid_owner.username, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "2️⃣":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = valor_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees - 2
                    update_raid = f'UPDATE "Raid-Events" SET total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=raid_owner.username, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass

        if event.emoji_name == "3️⃣":
            if instinct_present is None:
                instinct_present = "\u200b"
            else: 
                instinct_present = instinct_present.split(",")
            if mystic_present is None:
                mystic_present = "\u200b"
            else: 
                mystic_present = mystic_present.split(",")
            if valor_present is None:
                valor_present = "\u200b"
            else: 
                valor_present = valor_present.split(",")
            if remote_present is None:
                remote_present = "\u200b"
            else: 
                remote_present = valor_present.split(",")
            
            # UPDATE DATABASE
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    new_total_attendees = total_attendees - 3
                    update_raid = f'UPDATE "Raid-Events" SET total_attendees = {new_total_attendees} WHERE guild_id = {event.guild_id} AND channel_id = {event.channel_id} AND message_id = {event.message_id}'
                    await conn.fetch(update_raid)
            await database.close()

            location_exists, latitude, longitude = await validate.__validate_location(guild_id=event.guild_id, location=location)
            success, poke_img = await pokemon.get_pokemon_img(boss=boss)

            # EDIT MESSAGE
            embed = (
                hikari.Embed(
                    description=lang.raid_embed_description.format(raid_id=raid_id, time=f"{datetime.datetime.strptime(str(time), '%H:%M').strftime('%H:%M')} - {gmt}", date=datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d-%m-%Y'), location=location, latitude=latitude, longitude=longitude, raid_type=raid_type)
                )
                    .set_author(name=boss, icon=poke_img)
                    .set_footer(
                    text=lang.raid_embed_footer.format(member=raid_owner.username, attendees=new_total_attendees),
                )
                    .set_thumbnail(poke_img)
                    .add_field(name="Instinct:", value=", ".join(user for user in instinct_present), inline=False)
                    .add_field(name="Mystic:", value=", ".join(user for user in mystic_present), inline=False)
                    .add_field(name="Valor:", value=", ".join(user for user in valor_present), inline=False)
                    .add_field(name="Remote:", value=",".join(user for user in remote_present), inline=False)
            )
            
            try:
                raid_message_to_edit = await event.app.rest.fetch_message(channel=channel_id, message=message_id)
                await raid_message_to_edit.edit(embed=embed)
            except hikari.NotFoundError:
                pass


# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
    client.add_component(raid_component.copy())
    client.events.subscribe(hikari.GuildReactionAddEvent, on_guild_reaction_add)
    client.events.subscribe(hikari.GuildReactionDeleteEvent, on_guild_reaction_delete)