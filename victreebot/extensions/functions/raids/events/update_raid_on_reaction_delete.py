# Copyright (c) 2022-present l3keboy

import time

import hikari
import lightbulb

from victreebot.core.bot import Bot

loader = lightbulb.Loader()


@loader.listener(hikari.GuildReactionDeleteEvent)
async def update_raid_on_reaction_delete(event: hikari.GuildReactionDeleteEvent, bot: Bot) -> None:
    """Event to update the raid when someone removes a reaction to the message."""
    member = bot.cache.get_member(event.guild_id, event.user_id)
    if member is None or member.is_bot:
        return

    guild_settings = await bot.database.get_guild_settings(event.guild_id)
    if guild_settings is None:
        return

    raid = await bot.database.get_raid_by_message_id(event.guild_id, event.message_id)
    if raid is None:
        return

    raid_class = bot.raids.get(raid.raid_id)
    if raid_class is None:
        return

    if event.emoji_id == guild_settings.instinct_emoji_id and raid.end_time - time.time() > int(
        guild_settings.raid_timeout
    ):
        await raid_class.update_raid_from_reaction("instinct", add=False, member=member)
    if event.emoji_id == guild_settings.mystic_emoji_id and raid.end_time - time.time() > int(
        guild_settings.raid_timeout
    ):
        await raid_class.update_raid_from_reaction("mystic", add=False, member=member)
    if event.emoji_id == guild_settings.valor_emoji_id and raid.end_time - time.time() > int(
        guild_settings.raid_timeout
    ):
        await raid_class.update_raid_from_reaction("valor", add=False, member=member)
    if event.emoji_name == "1️⃣" and raid.end_time - time.time() > int(guild_settings.raid_timeout):
        await raid_class.update_raid_from_reaction("one", add=False, member=member)
    if event.emoji_name == "2️⃣" and raid.end_time - time.time() > int(guild_settings.raid_timeout):
        await raid_class.update_raid_from_reaction("two", add=False, member=member)
    if event.emoji_name == "3️⃣" and raid.end_time - time.time() > int(guild_settings.raid_timeout):
        await raid_class.update_raid_from_reaction("three", add=False, member=member)
    if event.emoji_name == "🇷" and raid.end_time - time.time() > int(guild_settings.raid_timeout):
        await raid_class.update_raid_from_reaction("remote", add=False, member=member)
