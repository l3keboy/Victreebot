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
from dotenv import load_dotenv
# Hikari
import hikari
import tanjun
# Functionality
import asyncio
import datetime
# Own Files
from utils import LoggingHandler 
from utils.functions import get_settings, get_profile, stats

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
# STATS GROUP COMMAND #
# ------------------------------------------------------------------------- #
stats_group = tanjun.slash_command_group("stats", f"Get the stats of a user or server.")
stats_component = tanjun.Component().add_slash_command(stats_group)


@stats_group.with_command
@tanjun.as_slash_command("server", "Get the stats of the server.")
async def command_stats_server(ctx: tanjun.abc.Context):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        stats_raids_created, stats_raids_deleted, stats_raids_completed = await stats.get_all_server_stats(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    if auto_delete_time < 15:
        auto_delete_this_message = 15
    else:
        auto_delete_this_message = auto_delete_time

    guild = await ctx.rest.fetch_guild(ctx.guild_id)
    embed = (
        hikari.Embed(
            title=lang.server_stats_embed_title.format(guild_name=guild.name),
            description=lang.server_stats_embed_description.format(guild_name=guild.name),
        )
            .set_footer(
            text=lang.embed_footer.format(member=ctx.member.display_name, auto_delete_time=auto_delete_this_message),
            icon=ctx.member.avatar_url,
        )
            .set_thumbnail()
            .add_field(name=lang.server_stats_embed_raids_created_title, value=lang.server_stats_embed_raids_created_description.format(raids_created=stats_raids_created), inline=True)
            .add_field(name=lang.server_stats_embed_raids_deleted_title, value=lang.server_stats_embed_raids_deleted_description.format(raids_deleted=stats_raids_deleted), inline=True)
            .add_field(name=lang.server_stats_embed_raids_completed_title, value=lang.server_stats_embed_raids_completed_description.format(raids_completed=stats_raids_completed), inline=True)
            .add_field(name="\n\u200b", value=f"\n\u200b", inline=False)    
    )

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_server_stats_requested.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    message = await ctx.respond(embed=embed, ensure_result=True)
    await asyncio.sleep(auto_delete_this_message)
    await message.delete()

@stats_group.with_command
@tanjun.with_user_slash_option("user", "The user to get the stats of.")
@tanjun.as_slash_command("user", "Get the stats of a user.")
async def command_stats_server(ctx: tanjun.abc.Context, user):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        stats_raids_created, stats_raids_participated = await stats.get_all_user_stats(guild_id=ctx.guild_id, user_id=user.id)
        friend_codes, location = await get_profile.get_all_profile_details(guild_id=ctx.guild_id, user_id=user.id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    if auto_delete_time < 15:
        auto_delete_this_message = 15
    else:
        auto_delete_this_message = auto_delete_time

    embed = (
        hikari.Embed(
            title=lang.user_stats_embed_title.format(user_name=user.username),
            description=lang.user_stats_embed_description.format(user_name=user.username),
        )
            .set_footer(
            text=lang.embed_footer.format(member=ctx.member.display_name, auto_delete_time=auto_delete_this_message),
            icon=ctx.member.avatar_url,
        )
            .set_thumbnail()
            .add_field(name=lang.user_stats_embed_raids_created_title, value=lang.user_stats_embed_raids_created_description.format(raids_created=stats_raids_created), inline=True)
            .add_field(name=lang.user_stats_embed_raids_participated_title, value=lang.user_stats_embed_raids_participated_description.format(raids_participated=stats_raids_participated), inline=True)
            .add_field(name="\n\u200b", value=f"\n\u200b", inline=False)
    )
    if location is None or location == []:
        embed.add_field(name=lang.user_stats_embed_user_locations_title, value=lang.user_stats_embed_no_locations_set, inline=False)
    else:
        location_list = location.split(",")
        embed.add_field(name=lang.user_stats_embed_user_locations_title, value=" - ".join(location for location in location_list), inline=False)

    if friend_codes is None or friend_codes == []:
        embed.add_field(name=lang.user_stats_embed_user_friend_codes_title, value=lang.user_stats_embed_no_friend_codes_set, inline=False)
    else:
        friend_codes_list = friend_codes.split(",")
        embed.add_field(name=lang.user_stats_embed_user_friend_codes_title, value=" - ".join(friend_code for friend_code in friend_codes_list), inline=False)
    embed.add_field(name="\n\u200b", value=f"\n\u200b", inline=False)    

    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_user_stats_requested.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member, user_name=user.username))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    # SEND RESPONSE
    message = await ctx.respond(embed=embed, ensure_result=True)
    await asyncio.sleep(auto_delete_this_message)
    await message.delete()


# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
    client.add_component(stats_component.copy())