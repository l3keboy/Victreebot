# Copyright (c) 2022-present l3keboy

import hikari
import lightbulb

from victreebot.core.bot import Bot

loader = lightbulb.Loader()


@loader.listener(hikari.GuildLeaveEvent)
async def remove_guild(event: hikari.GuildLeaveEvent, bot: Bot) -> None:
    """Event to remove a guild and its associated data."""
    # Get guild info
    guild = await bot.database.get_guild(guild_id=event.guild_id)
    guild_settings = await bot.database.get_guild_settings(guild_id=event.guild_id)
    guild_log_settings = await bot.database.get_guild_log_settings(guild_id=event.guild_id)
    guild_stats = await bot.database.get_guild_stats(guild_id=event.guild_id)

    # Remove server from database
    if guild:
        await bot.database.delete_guild(guild)
    if guild_settings:
        await bot.database.delete_guild_settings(guild_settings)
    if guild_log_settings:
        await bot.database.delete_guild_log_settings(guild_log_settings)
    if guild_stats:
        await bot.database.delete_guild_stats(guild_stats)

    guild_users = await bot.database.get_users_for_guild(guild_id=event.guild_id)
    if guild_users:
        await bot.database.delete_users(guild_users)

    locations = await bot.database.get_locations_for_guild(guild_id=event.guild_id)
    if locations:
        await bot.database.delete_locations(locations)

    raids = await bot.database.get_raids_for_guild(guild_id=event.guild_id)
    if raids:
        await bot.database.delete_raids(raids)
