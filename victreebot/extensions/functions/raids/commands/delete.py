import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.extensions.functions.raids.autocomplete.autocomplete_raid_id import autocomplete_raid_id
from victreebot.languages import en
from victreebot.extensions.functions.raids.commands import group
from victreebot.models.GuildStats import Guild_StatsUpdate

# Load command
loader = lightbulb.Loader()
loader.command(group)


# Command
@group.register
class RaidsDelete(
    lightbulb.SlashCommand, 
    name="delete", 
    description="Delete a raid",
):
    """Command to delete a raid."""

    raid_id: str = lightbulb.string(
        "raid_id",
        "The ID of the raid to delete",
        autocomplete=autocomplete_raid_id,  # type: ignore[arg-type]  # mypy: ignore
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

        raid = bot.raids.get(self.raid_id)
        if raid is None:
            response_message = await ctx.respond(language_helper.response_raid_delete_no_raid_found, components=[], embeds=[])
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_raid_delete_no_raid_found.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                    member=ctx.member,
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        if ctx.user.id != raid.raid_creator_id and (ctx.member is not None and guild_settings.moderator_role_id not in ctx.member.role_ids):
            response_message = await ctx.respond(language_helper.response_raid_delete_not_creator_or_moderator.format(bot_name=bot.vars.BOT_NAME.capitalize()), components=[], embeds=[])
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_raid_delete_not_creator_or_moderator.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                    member=ctx.member,
                    bot_name=bot.vars.BOT_NAME.capitalize(),
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        await raid.delete_raid()

        new_guild_stats = Guild_StatsUpdate(guild_id=ctx.guild_id, raids_deleted=int(guild_stats.raids_deleted) + 1)
        await bot.database.change_guild_stats_settings(guild_stats, new_guild_stats)

        response_message = await ctx.respond(language_helper.response_raid_delete_success, components=[], embeds=[])
        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
        if guild_log_settings.log_raid_delete:
            log_response = language_helper.log_response_raid_delete_success.format(
                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                member=ctx.member,
            )
            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
