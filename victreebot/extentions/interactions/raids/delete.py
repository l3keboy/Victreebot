# IMPORTS
import os

import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.autocomplete_callbacks import autocomplete_raid_id
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.with_str_slash_option("raid_id", "The ID of the raid to delete", autocomplete=autocomplete_raid_id)
@tanjun.as_slash_command("delete", "Delete a raid.")
async def command_raid_delete(
    ctx: tanjun.abc.SlashContext,
    raid_id: str,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, is_setup, moderator_role_id, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup", "moderator_role_id"]
    )
    log_errors, log_raid_delete, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_raid_delete"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    raid = bot_aware.raids.get(f"'{raid_id}'")
    if raid is None:
        response = SUPPORTED_LANGUAGES.get(language).response_raid_delete_no_raid_found
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_delete_no_raid_found.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return

    if ctx.author.id != raid.raid_creator_id and ctx.author.id != moderator_role_id:
        response = SUPPORTED_LANGUAGES.get(language).response_raid_delete_not_creator_or_moderator.format(
            bot_name=BOT_NAME.capitalize()
        )
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_delete_not_creator_or_moderator.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, bot_name=BOT_NAME.capitalize()
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return

    await raid.delete_raid()

    raids_deleted, *none = await db.get_guild_stats(ctx.get_guild(), stats=["raids_deleted"])
    new_raids_deleted = int(raids_deleted) + 1
    await db.set_guild_stats(ctx.get_guild(), parameters=[f"raids_deleted = {new_raids_deleted}"])

    response = SUPPORTED_LANGUAGES.get(language).response_raid_delete_success
    await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
    if log_raid_delete:
        log_response = SUPPORTED_LANGUAGES.get(language).log_response_raid_delete_success.format(
            datetime=await bot.get_timestamp_aware(gmt),
            member=ctx.member,
        )
        await bot.log_from_ctx(ctx, db, log_response)
