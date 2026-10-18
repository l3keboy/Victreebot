# Copyright (c) 2022-present l3keboy

import time

import hikari
import lightbulb

from victreebot.core.bot import Bot

loader = lightbulb.Loader()


@loader.listener(hikari.GuildReactionAddEvent)
async def update_raid_on_reaction_add(event: hikari.GuildReactionAddEvent, bot: Bot) -> None:
    """Event to update the raid when someone reacts to the message."""
    member = bot.cache.get_member(event.guild_id, event.user_id)
    if member is None or member.is_bot:
        return

    guild_settings = await bot.database.get_guild_settings(event.guild_id)
    if guild_settings is None:
        return

    raid = await bot.database.get_raid_by_message_id(event.guild_id, event.message_id)
    if raid is None:
        return

    message = bot.cache.get_message(event.message_id) or await bot.discord_service.get_message(
        event.channel_id, event.message_id
    )
    if message is None:
        return

    raid_class = bot.raids.get(raid.raid_id)
    if raid_class is None:
        return

    if event.emoji_id == guild_settings.instinct_emoji_id:
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raid_class.update_raid_from_reaction("instinct", add=True, member=event.member)
        elif guild_settings.instinct_emoji_id is not None:
            emoji = bot.cache.get_emoji(guild_settings.instinct_emoji_id) or await bot.discord_service.get_emoji(
                event.guild_id, guild_settings.instinct_emoji_id
            )
            if emoji is not None:
                await message.remove_reaction(emoji, user=event.member)
    if event.emoji_id == guild_settings.mystic_emoji_id:
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raid_class.update_raid_from_reaction("mystic", add=True, member=event.member)
        elif guild_settings.mystic_emoji_id is not None:
            emoji = bot.cache.get_emoji(guild_settings.mystic_emoji_id) or await bot.discord_service.get_emoji(
                event.guild_id, guild_settings.mystic_emoji_id
            )
            if emoji is not None:
                await message.remove_reaction(emoji, user=event.member)
    if event.emoji_id == guild_settings.valor_emoji_id:
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raid_class.update_raid_from_reaction("valor", add=True, member=event.member)
        elif guild_settings.valor_emoji_id is not None:
            emoji = bot.cache.get_emoji(guild_settings.valor_emoji_id) or await bot.discord_service.get_emoji(
                event.guild_id, guild_settings.valor_emoji_id
            )
            if emoji is not None:
                await message.remove_reaction(emoji, user=event.member)
    if event.emoji_name == "1️⃣":
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raid_class.update_raid_from_reaction("one", add=True, member=event.member)
        else:
            await message.remove_reaction("1️⃣", user=event.member)
    if event.emoji_name == "2️⃣":
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raid_class.update_raid_from_reaction("two", add=True, member=event.member)
        else:
            await message.remove_reaction("2️⃣", user=event.member)
    if event.emoji_name == "3️⃣":
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raid_class.update_raid_from_reaction("three", add=True, member=event.member)
        else:
            await message.remove_reaction("3️⃣", user=event.member)
    if event.emoji_name == "🇷":
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raid_class.update_raid_from_reaction("remote", add=True, member=event.member)
        else:
            await message.remove_reaction("🇷", user=event.member)
