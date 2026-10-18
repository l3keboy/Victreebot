# Copyright (c) 2022-present l3keboy

import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.contants import SUPPORTED_UNIT_SYSTEMS
from victreebot.core.bot import Bot
from victreebot.exceptions import DatabaseError
from victreebot.extensions.functions.settings.autocomplete.autocomplete_supported_timezones import (
    autocomplete_supported_timezones,
)
from victreebot.extensions.functions.settings.commands import group
from victreebot.extensions.functions.settings.commands import subgroup
from victreebot.languages import en
from victreebot.models.GuildSettings import Guild_SettingsUpdate

# Load command
loader = lightbulb.Loader()
loader.command(group)


# Command
@subgroup.register
class SettingsUpdateGeneral(
    lightbulb.SlashCommand,
    name="general",
    description="Update general settings",
    hooks=[lightbulb.prefab.has_permissions(hikari.Permissions.MANAGE_GUILD)],
):
    """Command to update the bots general settings."""

    language: str | None = lightbulb.string(
        "language",
        "The new language to respond in.",
        choices=[lightbulb.Choice(language, language) for language in SUPPORTED_LANGUAGES],
        default=None,
    )
    timezone: str | None = lightbulb.string(
        "timezone", "The timezone of the server", autocomplete=autocomplete_supported_timezones, default=None
    )
    unit_system: str | None = lightbulb.string(
        "unit_system",
        "The desired unit system of the server",
        choices=[lightbulb.Choice(system, system) for system in SUPPORTED_UNIT_SYSTEMS],
        default=None,
    )
    auto_delete: int | None = lightbulb.integer(
        "auto_delete",
        "The time before deleting responses automatically. 0 = don't delete responses.",
        default=None,
        min_value=0,
        max_value=900,
    )
    moderator_role: hikari.Role | None = lightbulb.role(
        "moderator_role", "The moderator role for the bot", default=None
    )

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

        # Create language helper
        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)
        auto_delete_helper = await bot.utils.determine_auto_delete(guild_settings.auto_delete)

        if not guild_settings.is_setup:
            response_message = await ctx.respond(
                language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize())
            )
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        if (
            self.language is None
            and self.timezone is None
            and self.unit_system is None
            and self.auto_delete is None
            and self.moderator_role is None
        ):
            response_message = await ctx.respond(language_helper.error_response_settings_update_insert_at_least_1)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_settings_update_general_failed.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        new_settings = Guild_SettingsUpdate(guild_id=ctx.guild_id)
        if self.language is not None:
            new_settings.language = self.language
        if self.timezone is not None:
            new_settings.gmt = self.timezone
        if self.unit_system is not None:
            new_settings.unit_system = self.unit_system
        if self.auto_delete is not None:
            new_settings.auto_delete = None if self.auto_delete == 0 else self.auto_delete
        if self.moderator_role is not None:
            new_settings.moderator_role_id = self.moderator_role.id

        try:
            guild_settings = await bot.database.change_guild_settings(guild_settings, new_settings)
        except DatabaseError:
            response_message = await ctx.respond(language_helper.response_settings_update_general_failed)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_settings_update_general_failed.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            raise

        response_message = await ctx.respond(language_helper.response_settings_update_general_success)
        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
        if guild_log_settings.log_settings_changed:
            log_response = language_helper.log_response_settings_update_general_success.format(
                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
            )
            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
