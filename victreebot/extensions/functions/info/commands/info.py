import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.languages import en

# Load command
loader = lightbulb.Loader()


# Command
@loader.command
class Pokedex(
    lightbulb.SlashCommand, 
    name="info", 
    description="Get the bots server info",
):
    """Command to get info about the bots settings."""

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context, bot: Bot) -> None:
        """Handle command interaction."""
        await ctx.defer()
        if ctx.guild_id is None:
            await ctx.respond("Command must be executed in a server.")
            return

        guild_settings = await bot.database.get_guild_settings(ctx.guild_id)
        if guild_settings is None:
            await ctx.respond("Command must be executed in a server.")
            return

        guild_log_settings = await bot.database.get_guild_log_settings(ctx.guild_id)
        if guild_log_settings is None:
            await ctx.respond("Command must be executed in a server.")
            return

        guild_stats = await bot.database.get_guild_stats(ctx.guild_id)
        if guild_stats is None:
            await ctx.respond("Command must be executed in a server.")
            return

        # Create language helper
        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
        auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)

        if not guild_settings.is_setup:
            response_message = await ctx.respond(language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize()))
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        channel_raids, channel_logs = None, None
        if guild_settings.raids_channel_id is not None:
            channel_raids = bot.cache.get_guild_channel(guild_settings.raids_channel_id) or await bot.discord_service.get_guild_channel(guild_settings.raids_channel_id)
        if guild_log_settings.logs_channel_id is not None:
            channel_logs = bot.cache.get_guild_channel(guild_log_settings.logs_channel_id) or await bot.discord_service.get_guild_channel(guild_log_settings.logs_channel_id)

        role_moderator, role_instinct, role_mystic, role_valor = None, None, None, None
        if guild_settings.moderator_role_id is not None:
            role_moderator = bot.cache.get_role(guild_settings.moderator_role_id) or await bot.discord_service.get_guild_role(ctx.guild_id, guild_settings.moderator_role_id)
        if guild_settings.instinct_role_id is not None:
            role_instinct = bot.cache.get_role(guild_settings.instinct_role_id) or await bot.discord_service.get_guild_role(ctx.guild_id, guild_settings.instinct_role_id)
        if guild_settings.mystic_role_id is not None:
            role_mystic = bot.cache.get_role(guild_settings.mystic_role_id) or await bot.discord_service.get_guild_role(ctx.guild_id, guild_settings.mystic_role_id)
        if guild_settings.valor_role_id is not None:
            role_valor = bot.cache.get_role(guild_settings.valor_role_id) or await bot.discord_service.get_guild_role(ctx.guild_id, guild_settings.valor_role_id)

        emoji_instinct, emoji_mystic, emoji_valor = None, None, None
        if guild_settings.instinct_emoji_id is not None:
            emoji_instinct = bot.cache.get_emoji(guild_settings.instinct_emoji_id) or await bot.discord_service.get_emoji(ctx.guild_id, guild_settings.instinct_emoji_id)
        if guild_settings.mystic_emoji_id is not None:
            emoji_mystic = bot.cache.get_emoji(guild_settings.mystic_emoji_id) or await bot.discord_service.get_emoji(ctx.guild_id, guild_settings.mystic_emoji_id)
        if guild_settings.valor_emoji_id is not None:
            emoji_valor = bot.cache.get_emoji(guild_settings.valor_emoji_id) or await bot.discord_service.get_emoji(ctx.guild_id, guild_settings.valor_emoji_id)

        logged_events: list[str] = []
        if guild_log_settings.log_errors:
            logged_events.append(language_helper.log_errors)
        if guild_log_settings.log_info:
            logged_events.append(language_helper.log_info)
        if guild_log_settings.log_settings_changed:
            logged_events.append(language_helper.log_settings_changed)
        if guild_log_settings.log_profile_edit:
            logged_events.append(language_helper.log_profile_edit)
        if guild_log_settings.log_profile_view:
            logged_events.append(language_helper.log_profile_view)
        if guild_log_settings.log_location_add:
            logged_events.append(language_helper.log_location_add)
        if guild_log_settings.log_location_delete:
            logged_events.append(language_helper.log_location_delete)
        if guild_log_settings.log_location_edit:
            logged_events.append(language_helper.log_location_edit)
        if guild_log_settings.log_location_info:
            logged_events.append(language_helper.log_location_info)
        if guild_log_settings.log_location_list:
            logged_events.append(language_helper.log_location_list)
        if guild_log_settings.log_raid_create:
            logged_events.append(language_helper.log_raid_create)
        if guild_log_settings.log_raid_edit:
            logged_events.append(language_helper.log_raid_edit)
        if guild_log_settings.log_raid_delete:
            logged_events.append(language_helper.log_raid_delete)
        if guild_log_settings.log_trade_offer:
            logged_events.append(language_helper.log_trade_offer)
        if guild_log_settings.log_trade_proposal:
            logged_events.append(language_helper.log_trade_proposal)
        if guild_log_settings.log_trade_search:
            logged_events.append(language_helper.log_trade_search)

        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_title.format(bot_name=bot.vars.BOT_NAME.capitalize(), version=bot.version)),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_field_title_settings_general_title_settings),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_field_title_settings_general_description_settings.format(language=guild_settings.language, auto_delete=guild_settings.auto_delete, unit_system=guild_settings.unit_system, timezone=guild_settings.gmt, raid_timeout=guild_settings.raid_timeout, extended_time_format=guild_settings.extended_time_format)),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_field_title_settings_general_title_roles),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_field_title_settings_general_description_roles.format(instinct=role_instinct.mention if role_instinct else None, mystic=role_mystic.mention if role_mystic else None, valor=role_valor.mention if role_valor else None, moderator=role_moderator.mention if role_moderator else None)),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_field_title_settings_general_title_emojis),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_field_title_settings_general_description_emojis.format(instinct=emoji_instinct, mystic=emoji_mystic, valor=emoji_valor)),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_field_title_settings_general_title_channels),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_field_title_settings_general_description_channels.format(raids=channel_raids.mention if channel_raids else None, logs=channel_logs.mention if channel_logs else None)),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.info_bot_embed_field_title_settings_general_title_logged_events),
                    hikari.impl.TextDisplayComponentBuilder(content=", ".join("`" + event + "`" for event in logged_events[:50])),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.info_bot_embed_footer.format(
                            raids_completed=guild_stats.raids_completed, raids_deleted=guild_stats.raids_deleted, raids_created=guild_stats.raids_created
                        )
                    ),
                ]
            )
        ]

        auto_delete_helper = 45 if auto_delete_helper < 45 else auto_delete_helper
        response_message = await ctx.respond(components=components)
        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
        if guild_log_settings.log_info:
            log_response = language_helper.log_response_info_requested.format(
                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
            )
            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
        return
