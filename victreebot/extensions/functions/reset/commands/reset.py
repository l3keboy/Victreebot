import contextlib
import logging
from pathlib import Path

import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.languages import en
from victreebot.models.GuildSettings import Guild_SettingsUpdate
from victreebot.models.GuildLogSettings import Guild_Log_SettingsUpdate

# Load command
loader = lightbulb.Loader()


# Command
@loader.command
class Reset(
    lightbulb.SlashCommand, 
    name="reset", 
    description="Reset the settings to start a new setup",
    hooks=[lightbulb.prefab.has_permissions(hikari.Permissions.MANAGE_GUILD)]
):
    """Command to reset the bots settings."""

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

        if ctx.channel_id == guild_settings.raids_channel_id or ctx.channel_id == guild_log_settings.logs_channel_id:
            response_message = await ctx.respond(language_helper.response_reset_from_channel_not_possible)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.reset_validation_embed_title.format(bot_name=bot.vars.BOT_NAME.capitalize())
                    ),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.reset_validation_embed_description.format(bot_name=bot.vars.BOT_NAME.capitalize())
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.SUCCESS,
                                label=language_helper.yes,
                                custom_id="reset,yes",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.DANGER,
                                label=language_helper.no,
                                custom_id="reset,no",
                            ),
                        ]
                    ),
                ]
            )
        ]

        response_message = await ctx.respond(components=components)

        listening = True
        while listening:
            try:
                event = await bot.wait_for(
                    hikari.ComponentInteractionCreateEvent,
                    timeout=max(auto_delete_helper, 30),
                    predicate=lambda event: event.interaction.user.id == ctx.user.id,
                )

                command, action = event.interaction.custom_id.split(",")
                if command != "reset":
                    return

                await event.interaction.create_initial_response(6)
                if action == "yes":
                    starter_path = Path().cwd()
                    gif = Path(f"{starter_path}/assets/gifs/loading.gif")
                    components = [
                        hikari.impl.ContainerComponentBuilder(
                            accent_color=hikari.Colour(0x8BC683),
                            components=[
                                hikari.impl.TextDisplayComponentBuilder(
                                    content=language_helper.reset_started_embed_title.format(bot_name=bot.vars.BOT_NAME.capitalize())
                                ),
                                hikari.impl.TextDisplayComponentBuilder(
                                    content=language_helper.reset_started_embed_description.format(bot_name=bot.vars.BOT_NAME.capitalize())
                                ),
                                hikari.impl.MediaGalleryComponentBuilder(
                                    items=[
                                        hikari.impl.MediaGalleryItemBuilder(
                                            media=gif,
                                        )
                                    ]
                                ),
                            ]
                        )
                    ]
                    await ctx.edit_response(response_message, components=components, embeds=[])

                    # DELETE CUSTOM EMOJI'S
                    if guild_settings.instinct_emoji_id:
                        await bot.discord_service.delete_emoji(
                            ctx.guild_id, int(guild_settings.instinct_emoji_id), reason=f"{bot.vars.BOT_NAME.capitalize()} reset Handler -- Reset!"
                        )
                    if guild_settings.mystic_emoji_id:
                        await bot.discord_service.delete_emoji(
                            ctx.guild_id, int(guild_settings.mystic_emoji_id), reason=f"{bot.vars.BOT_NAME.capitalize()} reset Handler -- Reset!"
                        )
                    if guild_settings.valor_emoji_id:
                        await bot.discord_service.delete_emoji(
                            ctx.guild_id, int(guild_settings.valor_emoji_id), reason=f"{bot.vars.BOT_NAME.capitalize()} reset Handler -- Reset!"
                        )

                    # DELETE ROLES
                    if guild_settings.instinct_role_id:
                        await bot.discord_service.delete_role(
                            ctx.guild_id, int(guild_settings.instinct_role_id), reason=f"{bot.vars.BOT_NAME.capitalize()} reset Handler -- Reset!"
                        )
                    if guild_settings.mystic_role_id:
                        await bot.discord_service.delete_role(
                            ctx.guild_id, int(guild_settings.mystic_role_id), reason=f"{bot.vars.BOT_NAME.capitalize()} reset Handler -- Reset!"
                        )
                    if guild_settings.valor_role_id:
                        await bot.discord_service.delete_role(
                            ctx.guild_id, int(guild_settings.valor_role_id), reason=f"{bot.vars.BOT_NAME.capitalize()} reset Handler -- Reset!"
                        )
                    if guild_settings.moderator_role_id:
                        await bot.discord_service.delete_role(
                            ctx.guild_id, int(guild_settings.moderator_role_id), reason=f"{bot.vars.BOT_NAME.capitalize()} reset Handler -- Reset!"
                        )

                    # DELETE CHANNELS
                    if guild_settings.raids_channel_id:
                        await bot.discord_service.delete_channel(
                            int(guild_settings.raids_channel_id), reason=f"{bot.vars.BOT_NAME.capitalize()} reset Handler -- Reset!"
                        )
                    if guild_log_settings.logs_channel_id:
                        await bot.discord_service.delete_channel(
                            int(guild_log_settings.logs_channel_id), reason=f"{bot.vars.BOT_NAME.capitalize()} reset Handler -- Reset!"
                        )

                    new_guild_settings = Guild_SettingsUpdate(
                        guild_id=ctx.guild_id,
                        is_setup=False,
                        raids_channel_id=None,
                        moderator_role_id=None,
                        instinct_role_id=None,
                        mystic_role_id=None,
                        valor_role_id=None,
                        instinct_emoji_id=None,
                        mystic_emoji_id=None,
                        valor_emoji_id=None,
                    )
                    new_guild_log_settings = Guild_Log_SettingsUpdate(
                        guild_id=ctx.guild_id,
                        logs_channel_id=None,
                    )

                    await bot.database.change_guild_settings(guild_settings, new_guild_settings)
                    await bot.database.change_guild_log_settings(guild_log_settings, new_guild_log_settings)

                    components = [
                        hikari.impl.ContainerComponentBuilder(
                            accent_color=hikari.Colour(0x8BC683),
                            components=[
                                hikari.impl.TextDisplayComponentBuilder(
                                    content=language_helper.reset_finished_embed_title.format(bot_name=bot.vars.BOT_NAME.capitalize())
                                ),
                                hikari.impl.TextDisplayComponentBuilder(
                                    content=language_helper.reset_finished_embed_description.format(bot_name=bot.vars.BOT_NAME.capitalize())
                                )
                            ]
                        )
                    ]
                    await ctx.edit_response(response_message, components=components, embeds=[])
                    await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)

                if action == "no":
                    await ctx.edit_response(response_message, language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize()), components=[], embeds=[])
                    await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                    if guild_log_settings.log_errors:
                        log_response = language_helper.log_response_reset_cancelled.format(
                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                            member=ctx.member,
                            bot_name=bot.vars.BOT_NAME.capitalize(),
                        )
                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                listening = False
            except TimeoutError:
                await ctx.delete_response(response_message)
                listening = False
            except Exception:
                logging.getLogger(__name__).exception(
                    "An error occurred while listening for the info command!"
                )
                await ctx.delete_response(response_message)
                listening = False

        with contextlib.suppress(Exception):
            await ctx.delete_response(response_message)
            listening = False