# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import os

import hikari
import tanjun
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES
from utils.VersionHandler import VersionHandler

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# info #
# ------------------------------------------------------------------------- #
@tanjun.as_slash_command("info", f"Get {BOT_NAME.capitalize()}'s and the servers info.")
async def command_info(
    ctx: tanjun.abc.SlashContext,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
):
    (
        language,
        gmt,
        unit_system,
        auto_delete,
        raids_channel_id,
        is_setup,
        moderator_role_id,
        instinct_role_id,
        mystic_role_id,
        valor_role_id,
        instinct_emoji_id,
        mystic_emoji_id,
        valor_emoji_id,
        raid_timeout,
        *none,
    ) = await db.get_guild_settings(
        guild=ctx.get_guild(),
        settings=[
            "language",
            "gmt",
            "unit_system",
            "auto_delete",
            "raids_channel_id",
            "is_setup",
            "moderator_role_id",
            "instinct_role_id",
            "mystic_role_id",
            "valor_role_id",
            "instinct_emoji_id",
            "mystic_emoji_id",
            "valor_emoji_id",
            "raid_timeout",
        ],
    )
    (
        logs_channel_id,
        log_errors,
        log_info,
        log_settings_changed,
        log_profile_edit,
        log_profile_view,
        log_location_add,
        log_location_delete,
        log_location_edit,
        log_location_info,
        log_location_list,
        log_raid_create,
        log_raid_edit,
        log_raid_delete,
        log_trade_offer,
        log_trade_proposal,
        log_trade_search,
        *none,
    ) = await db.get_guild_log_settings(
        ctx.get_guild(),
        settings=[
            "logs_channel_id",
            "log_errors",
            "log_info",
            "log_settings_changed",
            "log_profile_edit",
            "log_profile_view",
            "log_location_add",
            "log_location_delete",
            "log_location_edit",
            "log_location_info",
            "log_location_list",
            "log_raid_create",
            "log_raid_edit",
            "log_raid_delete",
            "log_trade_offer",
            "log_trade_proposal",
            "log_trade_search",
        ],
    )
    raids_completed, raids_deleted, raids_created = await db.get_guild_stats(
        ctx.get_guild(), stats=["raids_completed", "raids_deleted", "raids_created"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    version = VersionHandler().version_full
    gmt = gmt
    unit_system = unit_system
    raid_timeout = raid_timeout

    channel_raids = ctx.cache.get_guild_channel(raids_channel_id) or await ctx.rest.fetch_channel(raids_channel_id)
    channel_logs = ctx.cache.get_guild_channel(logs_channel_id) or await ctx.rest.fetch_channel(logs_channel_id)

    guild_roles = await ctx.rest.fetch_roles(ctx.guild_id)
    for role in guild_roles:
        if role.id == moderator_role_id:
            role_moderator = role
        elif role.id == instinct_role_id:
            role_instinct = role
        elif role.id == mystic_role_id:
            role_mystic = role
        elif role.id == valor_role_id:
            role_valor = role

    emoji_instinct = ctx.cache.get_emoji(instinct_emoji_id) or await ctx.rest.fetch_emoji(
        ctx.guild_id, instinct_emoji_id
    )
    emoji_mystic = ctx.cache.get_emoji(mystic_emoji_id) or await ctx.rest.fetch_emoji(ctx.guild_id, mystic_emoji_id)
    emoji_valor = ctx.cache.get_emoji(valor_emoji_id) or await ctx.rest.fetch_emoji(ctx.guild_id, valor_emoji_id)

    logged_events = []
    if log_errors:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_errors)
    if log_info:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_info)
    if log_settings_changed:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_settings_changed)
    if log_profile_edit:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_profile_edit)
    if log_profile_view:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_profile_view)
    if log_location_add:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_location_add)
    if log_location_delete:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_location_delete)
    if log_location_edit:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_location_edit)
    if log_location_info:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_location_info)
    if log_location_list:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_location_list)
    if log_raid_create:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_raid_create)
    if log_raid_edit:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_raid_edit)
    if log_raid_delete:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_raid_delete)
    if log_trade_offer:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_trade_offer)
    if log_trade_proposal:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_trade_proposal)
    if log_trade_search:
        logged_events.append(SUPPORTED_LANGUAGES.get(language).log_trade_search)

    auto_delete = 45 if auto_delete < 45 else auto_delete

    embed = (
        hikari.Embed(
            title=SUPPORTED_LANGUAGES.get(language).info_bot_embed_title.format(
                bot_name=BOT_NAME.capitalize(), version=version
            ),
        )
        .set_footer(
            text=SUPPORTED_LANGUAGES.get(language).info_bot_embed_footer.format(
                raids_completed=raids_completed, raids_deleted=raids_deleted, raids_created=raids_created
            ),
            icon=ctx.get_guild().icon_url,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_language,
            value=f"`{language}`",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_auto_delete,
            value=f"`{auto_delete} seconds`",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_unit_system,
            value=f"`{unit_system}`",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_gmt,
            value=f"`{gmt}`",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_timeout,
            value=f"`{raid_timeout} seconds`",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_moderator_role,
            value=f"{role_moderator.mention}",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_instinct_emoji,
            value=f"{emoji_instinct}",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_mystic_emoji,
            value=f"{emoji_mystic}",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_valor_emoji,
            value=f"{emoji_valor}",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_instinct_role,
            value=f"{role_instinct.mention}",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_mystic_role,
            value=f"{role_mystic.mention}",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_valor_role,
            value=f"{role_valor.mention}",
            inline=True,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_raids_channel,
            value=f"{channel_raids.mention}",
            inline=False,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_logging_channel,
            value=f"{channel_logs.mention}",
            inline=False,
        )
        .add_field(
            name=SUPPORTED_LANGUAGES.get(language).info_bot_embed_field_title_logging_events_1,
            value=", ".join("`" + event + "`" for event in logged_events[:50]),
            inline=False,
        )
    )

    await ctx.respond(embed=embed, delete_after=int(auto_delete))
    if log_info:
        # Send to log channel
        await bot.log_from_ctx(
            ctx,
            db,
            message=SUPPORTED_LANGUAGES.get(language).log_response_info_requested.format(
                datetime=await bot.get_timestamp(), member=ctx.member
            ),
        )
