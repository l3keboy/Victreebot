# Copyright (c) 2022-present l3keboy

import hikari
import lightbulb

from victreebot.core.bot import Bot

loader = lightbulb.Loader()


@loader.listener(hikari.GuildJoinEvent)
async def register_new_guild(event: hikari.GuildJoinEvent, bot: Bot) -> None:
    """Event to add a new guild default settings."""
    # Add server to database
    await bot.database.insert_guild(event.guild.id, event.guild.owner_id)
    await bot.database.insert_guild_settings(event.guild.id)
    await bot.database.insert_guild_log_settings(event.guild.id)
    await bot.database.insert_guild_stats(event.guild.id)

    # Add members to database
    members = (
        bot.cache.get_members_view_for_guild(event.guild.id).values()
        or await bot.discord_service.get_guild_members(event.guild.id)
        or []
    )
    for member in members:
        await bot.database.insert_user(event.guild.id, member.id)
