import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.exceptions import DatabaseError
from victreebot.extensions.functions.settings.commands import group
from victreebot.extensions.functions.settings.commands import subgroup
from victreebot.languages import en
from victreebot.models.GuildSettings import Guild_SettingsUpdate

# Load command
loader = lightbulb.Loader()
loader.command(group)


# Command
@subgroup.register
class SettingsUpdateRaid(
    lightbulb.SlashCommand, 
    name="raid", 
    description="Update raid settings",
    hooks=[lightbulb.prefab.has_permissions(hikari.Permissions.MANAGE_GUILD)]
):
    """Command to update the bots raids settings."""

    instinct_role: hikari.Role | None = lightbulb.role(
        "instinct_role",
        "The instinct role",
        default=None,
    )
    mystic_role: hikari.Role | None = lightbulb.role(
        "mystic_role",
        "The mystic role",
        default=None,
    )
    valor_role: hikari.Role | None = lightbulb.role(
        "valor_role",
        "The valor role",
        default=None,
    )
    instinct_emoji: str | None = lightbulb.string(
        "instinct_emoji",
        "The instinct emoji",
        default=None,
    )
    mystic_emoji: str | None = lightbulb.string(
        "mystic_emoji",
        "The mystic emoji",
        default=None,
    )
    valor_emoji: str | None = lightbulb.string(
        "valor_emoji",
        "The valor emoji",
        default=None,
    )
    raid_timeout: int | None = lightbulb.integer(
        "raid_timeout",
        "The time before raids get deleted after they have ended.",
        default=None,
        min_value=0,
    )
    extended_time_format: bool | None = lightbulb.boolean(
        "extended_time_format",
        "Do you want to use simple or extended time format?",
        default=None,
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
            response_message = await ctx.respond(language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize()))
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        if self.instinct_role is None and self.mystic_role is None and self.valor_role is None and self.instinct_emoji is None and self.mystic_emoji is None and self.valor_emoji is None and self.raid_timeout is None and self.extended_time_format is None:
            response_message = await ctx.respond(language_helper.error_response_settings_update_insert_at_least_1)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_settings_update_general_failed.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        filtered_raids = [raid for raid in bot.raids.values() if raid is not None and raid.guild_id == ctx.guild_id]
        if len(filtered_raids) > 0:
            response_message = await ctx.respond(language_helper.response_settings_update_raid_failed_raids_active)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_settings_update_raid_failed_raids_active.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        new_settings = Guild_SettingsUpdate(guild_id=ctx.guild_id)
        if self.instinct_role is not None:
            new_settings.instinct_role_id = self.instinct_role.id
        if self.mystic_role is not None:
            new_settings.mystic_role_id = self.mystic_role.id
        if self.valor_role is not None:
            new_settings.valor_role_id = self.valor_role.id
        if self.instinct_emoji is not None:
            instinct_emoji_id = filter(str.isdigit, self.instinct_emoji)
            instinct_emoji_id = "".join(instinct_emoji_id)
            emoji = bot.cache.get_emoji(int(instinct_emoji_id)) or await bot.discord_service.get_emoji(ctx.guild_id, int(instinct_emoji_id))
            if emoji is not None:
                new_settings.valor_role_id = emoji.id
        if self.mystic_emoji is not None:
            mystic_emoji_id = filter(str.isdigit, self.mystic_emoji)
            mystic_emoji_id = "".join(mystic_emoji_id)
            emoji = bot.cache.get_emoji(int(mystic_emoji_id)) or await bot.discord_service.get_emoji(ctx.guild_id, int(mystic_emoji_id))
            if emoji is not None:
                new_settings.mystic_emoji_id = emoji.id
        if self.valor_emoji is not None:
            valor_emoji_id = filter(str.isdigit, self.valor_emoji)
            valor_emoji_id = "".join(valor_emoji_id)
            emoji = bot.cache.get_emoji(int(valor_emoji_id)) or await bot.discord_service.get_emoji(ctx.guild_id, int(valor_emoji_id))
            if emoji is not None:
                new_settings.valor_emoji_id = emoji.id
        if self.raid_timeout is not None:
            new_settings.raid_timeout = self.raid_timeout
        if self.extended_time_format is not None:
            new_settings.extended_time_format = self.extended_time_format

        try:
            guild_settings = await bot.database.change_guild_settings(guild_settings, new_settings)
        except DatabaseError:
            response_message = await ctx.respond(language_helper.response_settings_update_raid_failed)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_settings_changed:
                log_response = language_helper.log_response_settings_update_raid_failed.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            raise
            
        response_message = await ctx.respond(language_helper.response_settings_update_raid_success)
        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
        if guild_log_settings.log_settings_changed:
            log_response = language_helper.log_response_settings_update_raid_success.format(
                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
            )
            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)