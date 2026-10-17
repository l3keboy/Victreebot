import hikari
import lightbulb

from victreebot.core.bot import Bot

loader = lightbulb.Loader()


@loader.listener(hikari.MemberCreateEvent)
async def register_new_member(event: hikari.MemberCreateEvent, bot: Bot) -> None:
    """Event to add a new member to the database."""
    # Add member to database
    await bot.database.insert_user(event.guild_id, event.user.id)