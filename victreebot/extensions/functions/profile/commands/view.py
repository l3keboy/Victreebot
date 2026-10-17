import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.languages import en
from victreebot.extensions.functions.profile.commands import group

# Load command
loader = lightbulb.Loader()
loader.command(group)


# Command
@group.register
class ProfileView(
    lightbulb.SlashCommand, 
    name="view", 
    description="View a profile",
):
    """Command to get info about a pokemon."""

    member: hikari.User | None = lightbulb.user(
        "member",
        "The member to view the profile off",
        default=None
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

        auto_delete_helper = 20 if auto_delete_helper < 20 else auto_delete_helper

        if self.member is None:
            self.member = ctx.member
        else:
            self.member = bot.cache.get_member(ctx.guild_id, self.member.id) or await bot.discord_service.get_member(ctx.guild_id, self.member.id)

        if self.member is None:
            response_message = await ctx.respond(language_helper.profile_no_member, components=[], embeds=[])
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_profile_no_member.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                    member=ctx.member,
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        user_details = await bot.database.get_user_for_guild(ctx.guild_id, self.member.id)
        if user_details is None:
            response_message = await ctx.respond(language_helper.profile_no_member, components=[], embeds=[])
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_profile_no_member.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                    member=ctx.member,
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        current_friend_codes_list = [language_helper.profile_no_friend_codes_set]
        if user_details.friend_codes is not None:
            current_friend_codes_list = user_details.friend_codes.split(",")
            
        current_active_locations_list = [language_helper.profile_no_active_locations_set]
        if user_details.active_locations is not None:
            current_active_locations_list = user_details.active_locations.split(",")
            
        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_view_embed_title),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_view_embed_description.format(member=self.member)),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_view_embed_field_friend_codes),
                    hikari.impl.TextDisplayComponentBuilder(content=", ".join(f"`{friend_code}`" for friend_code in current_friend_codes_list)),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_view_embed_field_active_locations),
                    hikari.impl.TextDisplayComponentBuilder(content=", ".join(f"`{location}`" for location in current_active_locations_list)),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_view_embed_field_raids_created),
                    hikari.impl.TextDisplayComponentBuilder(content=f"`{user_details.stats_raids_created} raids`"),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_view_embed_field_raids_participated),
                    hikari.impl.TextDisplayComponentBuilder(content=f"`{user_details.stats_raids_participated} raids`"),
                ]
            )
        ]

        if guild_log_settings.log_profile_view:
            log_response = language_helper.log_response_profile_view.format(
                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member, target_member=self.member
            )
            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

        auto_delete_helper = 20 if auto_delete_helper < 20 else auto_delete_helper
        response_message = await ctx.respond(components=components)
        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
