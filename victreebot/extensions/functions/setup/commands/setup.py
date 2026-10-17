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
class Setup(
    lightbulb.SlashCommand, 
    name="setup", 
    description="Setup basic settings to start using the bot",
    hooks=[lightbulb.prefab.has_permissions(hikari.Permissions.MANAGE_GUILD)]
):
    """Command to setup the bots settings."""

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

        if guild_settings.is_setup:
            response_message = await ctx.respond(language_helper.response_already_setup.format(bot_name=bot.vars.BOT_NAME.capitalize()))
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        my_user = bot.cache.get_me() or await bot.discord_service.get_my_user()
        if my_user is None:
            response_message = await ctx.respond(language_helper.response_setup_failed.format(bot_name=bot.vars.BOT_NAME.capitalize()))
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        starter_path = Path().cwd()
        gif = Path(f"{starter_path}/assets/gifs/loading.gif")
        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_started_embed_title.format(bot_name=bot.vars.BOT_NAME.capitalize())
                    ),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_started_embed_description.format(bot_name=bot.vars.BOT_NAME.capitalize())
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

        response_message = await ctx.respond(components=components)

        # UPLOAD CUSTOM EMOJI'S
        all_server_emojis = await bot.discord_service.get_guild_emojis(ctx.guild_id)
        for emoji in all_server_emojis:
            if (
                emoji.name == f"{bot.vars.BOT_NAME.lower()}_instinct"
                or emoji.name == f"{bot.vars.BOT_NAME.lower()}_mystic"
                or emoji.name == f"{bot.vars.BOT_NAME.lower()}_valor"
            ):
                await bot.discord_service.delete_emoji(ctx.guild_id, emoji.id, reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!")
                logging.getLogger(__name__).info(
                    "Deleted emoji with same name "
                    f"('{bot.vars.BOT_NAME.lower()}-instinct', '{bot.vars.BOT_NAME.lower()}-mystic' or '{bot.vars.BOT_NAME.lower()}-valor') "
                    f"for guild_id: {ctx.guild_id}!"
                )

        instinct_emoji, mystic_emoji, valor_emoji = None, None, None
        try:
            with open(Path(f"{starter_path}/assets/emojis/instinct.png"), "rb") as image:
                instinct_image_bytes = image.read()
                instinct_emoji = await bot.discord_service.create_emoji(
                    ctx.guild_id,
                    f"{bot.vars.BOT_NAME.lower()}_instinct",
                    instinct_image_bytes,
                    reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!",
                )
            with open(Path(f"{starter_path}/assets/emojis/mystic.png"), "rb") as image:
                mystic_image_bytes = image.read()
                mystic_emoji = await bot.discord_service.create_emoji(
                    ctx.guild_id,
                    f"{bot.vars.BOT_NAME.lower()}_mystic",
                    mystic_image_bytes,
                    reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!",
                )
            with open(Path(f"{starter_path}/assets/emojis/valor.png"), "rb") as image:
                valor_image_bytes = image.read()
                valor_emoji = await bot.discord_service.create_emoji(
                    ctx.guild_id,
                    f"{bot.vars.BOT_NAME.lower()}_valor",
                    valor_image_bytes,
                    reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!",
                )
            logging.getLogger(__name__).info(
                f"Added emoji's ('{bot.vars.BOT_NAME.lower()}-instinct', '{bot.vars.BOT_NAME.lower()}-mystic' "
                f" or '{bot.vars.BOT_NAME.lower()}-valor') to guild_id: {ctx.guild_id}!"
            )
        except Exception as e:
            logging.getLogger(__name__).error(
                "Unexpected error while trying to add one or more emoji's "
                f"('{bot.vars.BOT_NAME.lower()}_instinct', '{bot.vars.BOT_NAME.lower()}_mystic' or '{bot.vars.BOT_NAME.lower()}_valor') "
                f"for guild_id: {ctx.guild_id}! Got error: {e}"
            )

        # CREATE DEFAULT ROLES
        role_instinct_exists, role_mystic_exists, role_valor_exists, role_moderator_exists = False, False, False, False
        role_instinct, role_mystic, role_valor, role_moderator = None, None, None, None
        all_server_roles = await bot.discord_service.get_guild_roles(ctx.guild_id)
        for role in all_server_roles:
            if role.name == f"{bot.vars.BOT_NAME.capitalize()} instinct":
                logging.getLogger(__name__).info(
                    f"Role with name ('{bot.vars.BOT_NAME.lower()} instinct' exists in guild_id: {ctx.guild_id}! Continuing with existing role!"
                )
                role_instinct_exists, role_instinct = True, role
            if role.name == f"{bot.vars.BOT_NAME.capitalize()} mystic":
                logging.getLogger(__name__).info(
                    f"Role with name ('{bot.vars.BOT_NAME.lower()} mystic' exists in guild_id: {ctx.guild_id}! Continuing with existing role!"
                )
                role_mystic_exists, role_mystic = True, role
            if role.name == f"{bot.vars.BOT_NAME.capitalize()} valor":
                logging.getLogger(__name__).info(
                    f"Role with name ('{bot.vars.BOT_NAME.lower()} valor' exists in guild_id: {ctx.guild_id}! Continuing with existing role!"
                )
                role_valor_exists, role_valor = True, role
            if role.name == f"{bot.vars.BOT_NAME.capitalize()} moderator":
                logging.getLogger(__name__).info(
                    f"Role with name ('{bot.vars.BOT_NAME.lower()} moderator' exists in guild_id: {ctx.guild_id}! Continuing with existing role!"
                )
                role_moderator_exists, role_moderator = True, role

        if not role_instinct_exists:
            logging.getLogger(__name__).info(
                f"Role with name ('{bot.vars.BOT_NAME.lower()} instinct' doest not exist in guild_id: {ctx.guild_id}! Creating new role!"
            )
            role_instinct = await bot.discord_service.create_role(
                ctx.guild_id, 
                name=f"{bot.vars.BOT_NAME.capitalize()} instinct",
                colour=hikari.Colour(0xFDFF00),
                reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!",
            )
        if not role_mystic_exists:
            logging.getLogger(__name__).info(
                f"Role with name ('{bot.vars.BOT_NAME.lower()} mystic' doest not exist in guild_id: {ctx.guild_id}! Creating new role!"
            )
            role_mystic = await bot.discord_service.create_role(
                ctx.guild_id, 
                name=f"{bot.vars.BOT_NAME.capitalize()} mystic",
                colour=hikari.Colour(0x2A6CEB),
                reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!",
            )
        if not role_valor_exists:
            logging.getLogger(__name__).info(
                f"Role with name ('{bot.vars.BOT_NAME.lower()} valor' doest not exist in guild_id: {ctx.guild_id}! Creating new role!"
            )
            role_valor = await bot.discord_service.create_role(
                ctx.guild_id, 
                name=f"{bot.vars.BOT_NAME.capitalize()} valor",
                colour=hikari.Colour(0xFF0000),
                reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!",
            )
        if not role_moderator_exists:
            logging.getLogger(__name__).info(
                f"Role with name ('{bot.vars.BOT_NAME.lower()} moderator' doest not exist in guild_id: {ctx.guild_id}! Creating new role!"
            )
            role_moderator = await bot.discord_service.create_role(
                ctx.guild_id, 
                name=f"{bot.vars.BOT_NAME.capitalize()} moderator",
                colour=hikari.Colour(0xFFA500),
                reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!",
            )

        # CREATE DEFAULT CHANNELS
        channel_raids_exists, channel_logs_exists = False, False
        channel_raids, channel_logs = None, None
        all_server_channels = await bot.discord_service.get_guild_channels(ctx.guild_id)
        for channel in all_server_channels:
            if channel.name == f"{bot.vars.BOT_NAME.lower()}-raids":
                logging.getLogger(__name__).info(
                    f"Channel with name ('{bot.vars.BOT_NAME.lower()}-raids' exists in guild_id: {ctx.guild_id}! Continuing with existing channel!"
                )
                channel_raids_exists, channel_raids = True, channel
            if channel.name == f"{bot.vars.BOT_NAME.lower()}-logs":
                logging.getLogger(__name__).info(
                    f"Channel with name ('{bot.vars.BOT_NAME.lower()}-logs' exists in guild_id: {ctx.guild_id}! Continuing with existing channel!"
                )
                channel_logs_exists, channel_logs = True, channel

        permission_overwrites = [
            hikari.PermissionOverwrite(
                id=my_user.id,
                type=hikari.PermissionOverwriteType.MEMBER,
                allow=hikari.Permissions.MANAGE_CHANNELS | hikari.Permissions.SEND_MESSAGES,
            )
        ]
        if not channel_raids_exists:
            logging.getLogger(__name__).info(
                f"Channel with name ('{bot.vars.BOT_NAME.lower()}-raids' doest not exist in guild_id: {ctx.guild_id}! Creating new channel!"
            )
            channel_raids = await bot.discord_service.create_guild_text_channel(
                ctx.guild_id,
                name=f"{bot.vars.BOT_NAME.lower()}-raids",
                permission_overwrites=permission_overwrites,
                reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!",
            )
        if not channel_logs_exists:
            logging.getLogger(__name__).info(
                f"Channel with name ('{bot.vars.BOT_NAME.lower()}-logs' doest not exist in guild_id: {ctx.guild_id}! Creating new channel!"
            )
            channel_logs = await bot.discord_service.create_guild_text_channel(
                ctx.guild_id,
                name=f"{bot.vars.BOT_NAME.lower()}-logs",
                permission_overwrites=permission_overwrites,
                reason=f"{bot.vars.BOT_NAME.capitalize()} setup Handler -- Setup!",
            )

        if (channel_raids is None 
            or channel_logs is None 
            or role_moderator is None 
            or role_instinct is None 
            or role_mystic is None 
            or role_valor is None 
            or instinct_emoji is None 
            or mystic_emoji is None 
            or valor_emoji is None 
        ):
            logging.getLogger(__name__).info(
                f"Got None type for required variable. channel_raids: {channel_raids}, channel_logs: "
                f"{channel_logs}, role_moderator: {role_moderator}, role_instinct: {role_instinct}, "
                f"role_mystic: {role_mystic}, role_valor: {role_valor}, instinct_emoji: {instinct_emoji} "
                f"mystic_emoji: {mystic_emoji}, valor_emoji: {valor_emoji}"
            )
            await ctx.edit_response(language_helper.response_setup_failed.format(bot_name=bot.vars.BOT_NAME.capitalize()))
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        new_guild_settings = Guild_SettingsUpdate(
            guild_id=ctx.guild_id,
            is_setup=True,
            raids_channel_id=channel_raids.id,
            moderator_role_id=role_moderator.id,
            instinct_role_id=role_instinct.id,
            mystic_role_id=role_mystic.id,
            valor_role_id=role_valor.id,
            instinct_emoji_id=instinct_emoji,
            mystic_emoji_id=mystic_emoji,
            valor_emoji_id=valor_emoji
        )
        new_guild_log_settings = Guild_Log_SettingsUpdate(
            guild_id=ctx.guild_id,
            logs_channel_id=channel_logs.id
        )
        await bot.database.change_guild_settings(guild_settings, new_guild_settings)
        await bot.database.change_guild_log_settings(guild_log_settings, new_guild_log_settings)

        components_finished_overview = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_overview_title.format(bot_name=bot.vars.BOT_NAME.capitalize())
                    ),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_overview_description.format(
                            bot_name=bot.vars.BOT_NAME.capitalize(),
                            instinct_emoji=instinct_emoji,
                            mystic_emoji=mystic_emoji,
                            valor_emoji=valor_emoji,
                            role_instinct=role_instinct.mention,
                            role_mystic=role_mystic.mention,
                            role_valor=role_valor.mention,
                            role_moderator=role_moderator.mention,
                            channel_raids=channel_raids.mention,
                            channel_logs=channel_logs.mention
                        )
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_overview_field_1_title
                    ),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_overview_field_1_description.format(
                            bot_name=bot.vars.BOT_NAME.capitalize(),
                            language=guild_settings.language,
                            timezone=guild_settings.gmt,
                            unit_system=guild_settings.unit_system,
                            auto_delete=guild_settings.auto_delete,
                            channel_raids=channel_raids.mention,
                            channel_logs=channel_logs.mention,
                        )
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_overview_field_2_title.format(bot_name=bot.vars.BOT_NAME.capitalize())
                    ),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_overview_field_2_description.format(
                            bot_name=bot.vars.BOT_NAME.capitalize(),
                            support_server_link=bot.vars.SUPPORT_SERVER_LINK,
                            bot_invite_link=bot.vars.BOT_INVITE_LINK,
                        )
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_overview_footer.format(bot_name=bot.vars.BOT_NAME.capitalize())
                    ),
                ]
            )
        ]

        components_finished_message = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_finished_embed_title.format(bot_name=bot.vars.BOT_NAME.capitalize())
                    ),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.setup_finished_embed_description.format(bot_name=bot.vars.BOT_NAME.capitalize(), logs_channel_mention=channel_logs.mention)
                    )
                ]
            )
        ]

        await ctx.edit_response(response_message, components=components_finished_message, embeds=[])
        await bot.discord_service.create_message(channel_logs.id, None, components=components_finished_overview, embeds=[])
        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
