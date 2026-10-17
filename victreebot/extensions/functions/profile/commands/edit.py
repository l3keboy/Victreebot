import contextlib
import logging

import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.extensions.functions.profile.menus.friend_code_add_menu import FriendCodeAddModal
from victreebot.extensions.functions.profile.menus.friend_code_delete_menu import FriendCodeDeleteModal
from victreebot.extensions.functions.profile.menus.active_location_add_menu import ActiveLocationAddModal
from victreebot.extensions.functions.profile.menus.active_location_delete_menu import ActiveLocationDeleteModal
from victreebot.languages import en
from victreebot.extensions.functions.profile.commands import group
from victreebot.models.Users import UsersUpdate

# Load command
loader = lightbulb.Loader()
loader.command(group)


# Command
@group.register
class ProfileEdit(
    lightbulb.SlashCommand, 
    name="edit", 
    description="Edit your profile",
):
    """Command to edit your profile info."""

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

        current_user_details = await bot.database.get_user_for_guild(ctx.guild_id, ctx.user.id)
        if current_user_details is None:
            response_message = await ctx.respond(language_helper.profile_edit_no_member, components=[], embeds=[])
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_profile_edit_no_member.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                    member=ctx.member,
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        auto_delete_helper = 120 if auto_delete_helper < 120 else auto_delete_helper
        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_edit_embed_title),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_edit_embed_description),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.SUCCESS,
                                label=language_helper.profile_action_row_add_friend_code,
                                custom_id="profile,add_friend_codes",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.DANGER,
                                label=language_helper.profile_action_row_delete_friend_code,
                                custom_id="profile,delete_friend_codes",
                            ),
                        ]
                    ),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.SUCCESS,
                                label=language_helper.profile_action_row_add_active_location,
                                custom_id="profile,add_active_locations",
                            ),
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.DANGER,
                                label=language_helper.profile_action_row_delete_active_location,
                                custom_id="profile,delete_active_locations",
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
                if command != "profile":
                    return

                if action == "add_friend_codes":
                    friend_code_add_modal = FriendCodeAddModal(guild_settings.language)
                    await event.interaction.create_modal_response(
                        language_helper.profile_modal_add_friend_codes,
                        "friend_codes_add_modal",
                        components=friend_code_add_modal,
                    )

                    try:
                        await friend_code_add_modal.attach(bot.client, "friend_codes_add_modal", timeout=auto_delete_helper)
                    except TimeoutError:
                        await ctx.delete_response(response_message)
                        listening = False
                    else:
                        if friend_code_add_modal.selected_btn == "friend_codes_add_modal" and (
                            friend_code_add_modal.given_friend_code is not None
                        ):
                            current_friend_codes_list = []
                            if current_user_details.friend_codes is not None:
                                current_friend_codes_list = current_user_details.friend_codes.strip("'").split(",")

                            given_friend_codes_list = friend_code_add_modal.given_friend_code.split(",")

                            for friend_code in given_friend_codes_list:
                                friend_code = friend_code.replace("-", " ").lstrip().rstrip()
                                is_valid_friend_code = await bot.utils.validate_friend_code(friend_code)
                                if not is_valid_friend_code:
                                    components_error = [
                                        hikari.impl.ContainerComponentBuilder(
                                            accent_color=hikari.Colour(0x8BC683),
                                            components=[
                                                hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_edit_embed_title),
                                                hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_profile_edit_invalid_friend_code_format),
                                            ]
                                        )
                                    ]
                                    await ctx.edit_response(response_message, components=components_error, embeds=[])
                                    await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                                    if guild_log_settings.log_errors:
                                        log_response = language_helper.log_response_profile_edit_invalid_friend_code_format.format(
                                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                            member=ctx.member,
                                        )
                                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                                    return

                                if friend_code not in current_friend_codes_list:
                                    current_friend_codes_list.append(friend_code)

                            new_user_details = UsersUpdate(
                                guild_id=ctx.guild_id, 
                                user_id=ctx.user.id,
                                friend_codes=",".join(friend_code for friend_code in current_friend_codes_list)
                            )

                            await bot.database.change_user(current_user_details, new_user_details)

                            components_success = [
                                hikari.impl.ContainerComponentBuilder(
                                    accent_color=hikari.Colour(0x8BC683),
                                    components=[
                                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_edit_embed_title),
                                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_profile_edit_success),
                                    ]
                                )
                            ]
                            await ctx.edit_response(response_message, components=components_success, embeds=[])
                            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                            if guild_log_settings.log_profile_edit:
                                log_response = language_helper.log_response_profile_edit.format(
                                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                    member=ctx.member,
                                )
                                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                if action == "delete_friend_codes":
                    friend_code_delete_modal = FriendCodeDeleteModal(guild_settings.language)
                    await event.interaction.create_modal_response(
                        language_helper.profile_modal_delete_friend_codes,
                        "friend_codes_delete_modal",
                        components=friend_code_delete_modal,
                    )

                    try:
                        await friend_code_delete_modal.attach(bot.client, "friend_codes_delete_modal", timeout=auto_delete_helper)
                    except TimeoutError:
                        await ctx.delete_response(response_message)
                        listening = False
                    else:
                        if friend_code_delete_modal.selected_btn == "friend_codes_delete_modal" and (
                            friend_code_delete_modal.given_friend_code is not None
                        ):
                            current_friend_codes_list = []
                            if current_user_details.friend_codes is not None:
                                current_friend_codes_list = current_user_details.friend_codes.strip("'").split(",")

                            given_friend_codes_list = friend_code_delete_modal.given_friend_code.split(",")

                            for friend_code in given_friend_codes_list:
                                friend_code = friend_code.replace("-", " ").lstrip().rstrip()
                                is_valid_friend_code = await bot.utils.validate_friend_code(friend_code)
                                if not is_valid_friend_code:
                                    components_error = [
                                        hikari.impl.ContainerComponentBuilder(
                                            accent_color=hikari.Colour(0x8BC683),
                                            components=[
                                                hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_edit_embed_title),
                                                hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_profile_edit_invalid_friend_code_format),
                                            ]
                                        )
                                    ]
                                    await ctx.edit_response(response_message, components=components_error, embeds=[])
                                    await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                                    if guild_log_settings.log_errors:
                                        log_response = language_helper.log_response_profile_edit_invalid_friend_code_format.format(
                                            datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                            member=ctx.member,
                                        )
                                        await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                                    return

                                if friend_code in current_friend_codes_list:
                                    current_friend_codes_list.remove(friend_code)

                            new_user_details = UsersUpdate(
                                guild_id=ctx.guild_id, 
                                user_id=ctx.user.id,
                                friend_codes=None if len(current_friend_codes_list) <= 0 else ",".join(friend_code for friend_code in current_friend_codes_list)
                            )

                            await bot.database.change_user(current_user_details, new_user_details)

                            components_success = [
                                hikari.impl.ContainerComponentBuilder(
                                    accent_color=hikari.Colour(0x8BC683),
                                    components=[
                                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_edit_embed_title),
                                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_profile_edit_success),
                                    ]
                                )
                            ]
                            await ctx.edit_response(response_message, components=components_success, embeds=[])
                            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                            if guild_log_settings.log_profile_edit:
                                log_response = language_helper.log_response_profile_edit.format(
                                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                    member=ctx.member,
                                )
                                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                if action == "add_active_locations":
                    active_location_add_modal = ActiveLocationAddModal(guild_settings.language)
                    await event.interaction.create_modal_response(
                        language_helper.profile_modal_add_active_locations,
                        "active_locations_add_modal",
                        components=active_location_add_modal,
                    )

                    try:
                        await active_location_add_modal.attach(bot.client, "active_locations_add_modal", timeout=auto_delete_helper)
                    except TimeoutError:
                        await ctx.delete_response(response_message)
                        listening = False
                    else:
                        if active_location_add_modal.selected_btn == "active_locations_add_modal" and (
                            active_location_add_modal.given_active_location is not None
                        ):
                            current_active_locations_list = []
                            if current_user_details.active_locations is not None:
                                current_active_locations_list = current_user_details.active_locations.strip("'").split(",")

                            given_active_locations_list = active_location_add_modal.given_active_location.split(",")

                            for active_location in given_active_locations_list:
                                active_location = active_location.replace("-", " ").lstrip().rstrip()
                                if active_location not in current_active_locations_list:
                                    current_active_locations_list.append(active_location)

                            new_user_details = UsersUpdate(
                                guild_id=ctx.guild_id, 
                                user_id=ctx.user.id,
                                active_locations=",".join(location for location in current_active_locations_list)
                            )

                            await bot.database.change_user(current_user_details, new_user_details)

                            components_success = [
                                hikari.impl.ContainerComponentBuilder(
                                    accent_color=hikari.Colour(0x8BC683),
                                    components=[
                                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_edit_embed_title),
                                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_profile_edit_success),
                                    ]
                                )
                            ]
                            await ctx.edit_response(response_message, components=components_success, embeds=[])
                            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                            if guild_log_settings.log_profile_edit:
                                log_response = language_helper.log_response_profile_edit.format(
                                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                    member=ctx.member,
                                )
                                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                if action == "delete_active_locations":
                    active_location_delete_modal = ActiveLocationDeleteModal(guild_settings.language)
                    await event.interaction.create_modal_response(
                        language_helper.profile_modal_delete_active_locations,
                        "active_locations_delete_modal",
                        components=active_location_delete_modal,
                    )

                    try:
                        await active_location_delete_modal.attach(bot.client, "active_locations_delete_modal", timeout=auto_delete_helper)
                    except TimeoutError:
                        await ctx.delete_response(response_message)
                        listening = False
                    else:
                        if active_location_delete_modal.selected_btn == "active_locations_delete_modal" and (
                            active_location_delete_modal.given_active_location is not None
                        ):
                            current_active_locations_list = []
                            if current_user_details.active_locations is not None:
                                current_active_locations_list = current_user_details.active_locations.strip("'").split(",")

                            given_active_locations_list = active_location_delete_modal.given_active_location.split(",")
                            
                            for active_location in given_active_locations_list:
                                active_location = active_location.replace("-", " ").lstrip().rstrip()
                                if active_location in current_active_locations_list:
                                    current_active_locations_list.remove(active_location)

                            new_user_details = UsersUpdate(
                                guild_id=ctx.guild_id, 
                                user_id=ctx.user.id,
                                active_locations=None if len(current_active_locations_list) <= 0 else ",".join(location for location in current_active_locations_list)
                            )

                            await bot.database.change_user(current_user_details, new_user_details)

                            components_success = [
                                hikari.impl.ContainerComponentBuilder(
                                    accent_color=hikari.Colour(0x8BC683),
                                    components=[
                                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.profile_edit_embed_title),
                                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_profile_edit_success),
                                    ]
                                )
                            ]
                            await ctx.edit_response(response_message, components=components_success, embeds=[])
                            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                            if guild_log_settings.log_profile_edit:
                                log_response = language_helper.log_response_profile_edit.format(
                                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt),
                                    member=ctx.member,
                                )
                                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)

                listening = False
            except TimeoutError:
                await ctx.delete_response(response_message)
                listening = False
            except Exception:
                logging.getLogger(__name__).exception(
                    "An error occurred while listening for the profile edit command!"
                )
                await ctx.delete_response(response_message)
                listening = False

        with contextlib.suppress(Exception):
            await ctx.delete_response(response_message)
            listening = False
