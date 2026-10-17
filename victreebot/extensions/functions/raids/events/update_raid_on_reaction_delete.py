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

    raidClass = bot.raids.get(raid.raid_id)
    if raidClass is None:
        return

    if event.emoji_id == guild_settings.instinct_emoji_id:
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raidClass.update_raid_from_reaction("instinct", False, member)
    if event.emoji_id == guild_settings.mystic_emoji_id:
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raidClass.update_raid_from_reaction("mystic", False, member)
    if event.emoji_id == guild_settings.valor_emoji_id:
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raidClass.update_raid_from_reaction("valor", False, member)
    if event.emoji_name == "1️⃣":
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raidClass.update_raid_from_reaction("one", False, member)
    if event.emoji_name == "2️⃣":
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raidClass.update_raid_from_reaction("two", False, member)
    if event.emoji_name == "3️⃣":
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raidClass.update_raid_from_reaction("three", False, member)
    if event.emoji_name == "🇷":
        if raid.end_time - time.time() > int(guild_settings.raid_timeout):
            await raidClass.update_raid_from_reaction("remote", False, member)
