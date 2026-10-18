# Copyright (c) 2022-present l3keboy

import hikari
import lightbulb

from victreebot.core.bot import Bot

loader = lightbulb.Loader()


@loader.listener(hikari.MemberDeleteEvent)
async def remove_member(event: hikari.MemberDeleteEvent, bot: Bot) -> None:
    """Event to remove a member from the database."""
    # Get member from database
    member = await bot.database.get_user_for_guild(event.guild_id, event.user_id)
    if member:
        # Remove member from database
        await bot.database.delete_user(member)
