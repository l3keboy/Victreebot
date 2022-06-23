# IMPORTS
import os

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.with_member_slash_option("member", "The member to view the profile off", default=None)
@tanjun.as_slash_command("view", "View a profile")
async def command_profile_view(
    ctx: tanjun.abc.SlashContext,
    member: hikari.Member,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup"]
    )
    log_errors, log_profile_view, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_profile_view"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    auto_delete = 20 if auto_delete < 20 else auto_delete

    if member is None:
        member = ctx.member
    if member is not None:
        member = ctx.cache.get_member(ctx.guild_id, member) or await ctx.rest.fetch_member(ctx.guild_id, member)

    (
        current_friend_codes,
        current_active_locations,
        stats_raids_created,
        stats_raids_participated,
        *none,
    ) = await db.get_user_details(
        ctx.get_guild(),
        member,
        details=["friend_codes", "active_locations", "stats_raids_created", "stats_raids_participated"],
    )
    if current_friend_codes is not None and current_friend_codes != "NULL":
        current_friend_codes = current_friend_codes.strip("'")
        current_friend_codes_list = current_friend_codes.split(",")
    else:
        current_friend_codes_list = []
        current_friend_codes_list.append(SUPPORTED_LANGUAGES.get(language).profile_no_friend_codes_set)

    if current_active_locations is not None and current_active_locations != "NULL":
        current_active_locations = current_active_locations.strip("'")
        current_active_locations_list = current_active_locations.split(",")
    else:
        current_active_locations_list = []
        current_active_locations_list.append(SUPPORTED_LANGUAGES.get(language).profile_no_active_locations_set)

    embed = (
        hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).profile_view_embed_title,
            description=SUPPORTED_LANGUAGES.get(language).profile_view_embed_description.format(member=member),
            colour=hikari.Colour(0x8BC683),
        )
        .set_thumbnail(member.avatar_url)
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).profile_view_embed_field_friend_codes,
            value=", ".join(f"`{friend_code}`" for friend_code in current_friend_codes_list),
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).profile_view_embed_field_active_locations,
            value=", ".join(f"`{location}`" for location in current_active_locations_list),
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).profile_view_embed_field_raids_created,
            value=f"`{stats_raids_created} raids`",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).profile_view_embed_field_raids_participated,
            value=f"`{stats_raids_participated} raids`",
            inline=True,
        )
    )

    await ctx.respond(embed=embed, delete_after=auto_delete)
    if log_profile_view:
        log_response = SUPPORTED_LANGUAGES.get(language).log_response_profile_view.format(
            datetime=await bot.get_timestamp_aware(gmt), member=ctx.member, target_member=member
        )
        await bot.log_from_ctx(ctx, db, log_response)
