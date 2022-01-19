# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #
# IMPORTS
# Database and .env
import os
from dotenv import load_dotenv
# Hikari
import hikari
import tanjun
# Functionality
import asyncio
import datetime
# Own Files
from utils import LoggingHandler 
from utils.functions import get_settings

# .ENV AND .ENV VARIABLES
# Load .env
load_dotenv()
# Variables
# Bot Variables
BOT_NAME = os.getenv("BOT_NAME")

component = tanjun.Component()


# ------------------------------------------------------------------------- #
# SLASH COMMANDS #
# ------------------------------------------------------------------------- #
# ------------------------------------------------------------------------- #
# EXPLANATION GROUP COMMAND #
# ------------------------------------------------------------------------- #
explanation_group = tanjun.slash_command_group("explanation", f"Send explanation about a specified command to your DM.")
explanation_component = tanjun.Component().add_slash_command(explanation_group)


@explanation_group.with_command
@tanjun.as_slash_command("location", "Send the explanation of locations to your DM.")
async def command_explanation_raid(ctx: tanjun.abc.Context):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    # SEND RESPONSE
    try:
        response = lang.explanation_sending
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to respond to explanation raid init message! Got error: {e}")
        
    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_explanation_location_sending.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    bot_member = await ctx.rest.fetch_my_user()
    # SEND TO EXPLANATION CHANNEL
    explanation_raid_page_1 = (
        hikari.Embed(
            title=lang.explanation_location_page_1_title,
            description=lang.explanation_location_page_1_description
        )
            .set_author(name=lang.explanation_author, icon=bot_member.avatar_url)
            .set_footer(
            text=lang.explanation_embed_footer
        )
            .set_thumbnail()
    )

    explanation_raid_page_2 = (
        hikari.Embed(
            title=lang.explanation_location_page_2_title,
            description=lang.explanation_location_page_2_description
        )
            .set_author(name=lang.explanation_author, icon=bot_member.avatar_url)
            .set_footer(
            text=lang.explanation_embed_footer
        )
            .set_thumbnail()
            .add_field(name=lang.explanation_location_page_2_field_1_title, value=lang.explanation_location_page_2_field_1_value, inline=False)
    )

    explanation_raid_page_3 = (
        hikari.Embed(
            title=lang.explanation_location_page_3_title,
            description=lang.explanation_location_page_3_description
        )
            .set_author(name=lang.explanation_author, icon=bot_member.avatar_url)
            .set_footer(
            text=lang.explanation_embed_footer
        )
            .set_thumbnail()
            .add_field(name=lang.explanation_location_page_3_field_1_title, value=lang.explanation_location_page_3_field_1_value, inline=False)
            .add_field(name=lang.explanation_location_page_3_field_2_title, value=lang.explanation_location_page_3_field_2_value, inline=False)
    )

    explanation_raid_page_4 = (
        hikari.Embed(
            title=lang.explanation_location_page_4_title,
            description=lang.explanation_location_page_4_description
        )
            .set_author(name=lang.explanation_author, icon=bot_member.avatar_url)
            .set_footer(
            text=lang.explanation_embed_footer
        )
            .set_thumbnail()
            .add_field(name=lang.explanation_location_page_4_field_1_title, value=lang.explanation_location_page_4_field_1_value, inline=False)
            .add_field(name=lang.explanation_location_page_4_field_2_title, value=lang.explanation_location_page_4_field_2_value, inline=False)
    )

    values = [explanation_raid_page_1, explanation_raid_page_2, explanation_raid_page_3, explanation_raid_page_4]

    index = 0
    button_menu = (
        ctx.rest.build_action_row()
        .add_button(hikari.messages.ButtonStyle.SECONDARY, "<<")
        .set_label("<<")
        .add_to_container()
        .add_button(hikari.messages.ButtonStyle.PRIMARY, "<")
        .set_label("<")
        .add_to_container()
        .add_button(hikari.messages.ButtonStyle.PRIMARY, ">")
        .set_label(">")
        .add_to_container()
        .add_button(hikari.messages.ButtonStyle.SECONDARY, ">>")
        .set_label(">>")
        .add_to_container()
    )

    try:
        response_to_user = await ctx.member.send(values[0], component=button_menu)
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send explanation raid to DM for user_id: {ctx.member.id}!")
        # SEND TO LOG CHANNEL
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_explanation_location_sending_failed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    while True:
        try:
            event = await ctx.client.events.wait_for(hikari.InteractionCreateEvent, timeout=60)
        except asyncio.TimeoutError:
            await response_to_user.delete()
            return
        else:
            if isinstance(event.interaction, hikari.CommandInteraction):
                await response_to_user.delete()
                return
            elif event.interaction.custom_id == "<<":
                index = 0
            elif event.interaction.custom_id == "<":
                index = (index - 1) % len(values)
            elif event.interaction.custom_id == ">":
                index = (index + 1) % len(values)
            elif event.interaction.custom_id == ">>":
                index = len(values) - 1

            await response_to_user.edit(values[index])
            await event.interaction.create_initial_response(
                hikari.interactions.base_interactions.ResponseType.DEFERRED_MESSAGE_UPDATE,
                values[index]
            )

@explanation_group.with_command
@tanjun.as_slash_command("raid", "Send the explanation of raids to your DM.")
async def command_explanation_raid(ctx: tanjun.abc.Context):
    try:
        lang, auto_delete_time = await get_settings.get_language_auto_delete_time_settings(guild_id=ctx.guild_id)
        log_channel_id = await get_settings.get_log_channel_settings(guild_id=ctx.guild_id)
    except TypeError as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Type error, something wrong with database (IndexError?). Error: {e}")
        return

    # SEND RESPONSE
    try:
        response = lang.explanation_sending
        message = await ctx.respond(response, ensure_result=True)
        await asyncio.sleep(auto_delete_time)
        await message.delete()
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to respond to explanation raid init message! Got error: {e}")
        
    # SEND TO LOG CHANNEL
    try:
        channel = await ctx.rest.fetch_channel(channel=log_channel_id)
        await channel.send(lang.log_channel_explanation_raid_sending.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    bot_member = await ctx.rest.fetch_my_user()
    # SEND TO EXPLANATION CHANNEL
    explanation_raid_page_1 = (
        hikari.Embed(
            title=lang.explanation_raid_page_1_title,
            description=lang.explanation_raid_page_1_description
        )
            .set_author(name=lang.explanation_author, icon=bot_member.avatar_url)
            .set_footer(
            text=lang.explanation_embed_footer
        )
            .set_thumbnail()
    )

    explanation_raid_page_2 = (
        hikari.Embed(
            title=lang.explanation_raid_page_2_title,
            description=lang.explanation_raid_page_2_description
        )
            .set_author(name=lang.explanation_author, icon=bot_member.avatar_url)
            .set_footer(
            text=lang.explanation_embed_footer
        )
            .set_thumbnail()
            .add_field(name=lang.explanation_raid_page_2_field_1_title, value=lang.explanation_raid_page_2_field_1_value, inline=False)
            .add_field(name=lang.explanation_raid_page_2_field_2_title, value=lang.explanation_raid_page_2_field_2_value, inline=False)
            .add_field(name=lang.explanation_raid_page_2_field_3_title, value=lang.explanation_raid_page_2_field_3_value, inline=False)
    )

    explanation_raid_page_3 = (
        hikari.Embed(
            title=lang.explanation_raid_page_3_title,
            description=lang.explanation_raid_page_3_description
        )
            .set_author(name=lang.explanation_author, icon=bot_member.avatar_url)
            .set_footer(
            text=lang.explanation_embed_footer
        )
            .set_thumbnail()
            .add_field(name=lang.explanation_raid_page_3_field_1_title, value=lang.explanation_raid_page_3_field_1_value, inline=False)
            .add_field(name=lang.explanation_raid_page_3_field_2_title, value=lang.explanation_raid_page_3_field_2_value, inline=False)
    )

    explanation_raid_page_4 = (
        hikari.Embed(
            title=lang.explanation_raid_page_4_title,
            description=lang.explanation_raid_page_4_description
        )
            .set_author(name=lang.explanation_author, icon=bot_member.avatar_url)
            .set_footer(
            text=lang.explanation_embed_footer
        )
            .set_thumbnail()
            .add_field(name=lang.explanation_raid_page_4_field_1_title, value=lang.explanation_raid_page_4_field_1_value, inline=False)
            .add_field(name=lang.explanation_raid_page_4_field_2_title, value=lang.explanation_raid_page_4_field_2_value, inline=False)
            .add_field(name=lang.explanation_raid_page_4_field_3_title, value=lang.explanation_raid_page_4_field_3_value, inline=False)
    )

    explanation_raid_page_5 = (
        hikari.Embed(
            title=lang.explanation_raid_page_5_title,
            description=lang.explanation_raid_page_5_description
        )
            .set_author(name=lang.explanation_author, icon=bot_member.avatar_url)
            .set_footer(
            text=lang.explanation_embed_footer
        )
            .set_thumbnail()
            .add_field(name=lang.explanation_raid_page_5_field_1_title, value=lang.explanation_raid_page_5_field_1_value, inline=False)
            .add_field(name=lang.explanation_raid_page_5_field_2_title, value=lang.explanation_raid_page_5_field_2_value, inline=False)
    )

    values = [explanation_raid_page_1, explanation_raid_page_2, explanation_raid_page_3, explanation_raid_page_4, explanation_raid_page_5]

    index = 0
    button_menu = (
        ctx.rest.build_action_row()
        .add_button(hikari.messages.ButtonStyle.SECONDARY, "<<")
        .set_label("<<")
        .add_to_container()
        .add_button(hikari.messages.ButtonStyle.PRIMARY, "<")
        .set_label("<")
        .add_to_container()
        .add_button(hikari.messages.ButtonStyle.PRIMARY, ">")
        .set_label(">")
        .add_to_container()
        .add_button(hikari.messages.ButtonStyle.SECONDARY, ">>")
        .set_label(">>")
        .add_to_container()
    )

    try:
        response_to_user = await ctx.member.send(values[0], component=button_menu)
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send explanation raid to DM for user_id: {ctx.member.id}!")
        # SEND TO LOG CHANNEL
        try:
            channel = await ctx.rest.fetch_channel(channel=log_channel_id)
            await channel.send(lang.log_channel_explanation_raid_sending_failed.format(datetime=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), member=ctx.member))
        except Exception as e:
            LoggingHandler.LoggingHandler().logger_victreebot_logger.error(f"Something went wrong while trying to send to log channel for guild_id: {ctx.guild_id}!")

    while True:
        try:
            event = await ctx.client.events.wait_for(hikari.InteractionCreateEvent, timeout=60)
        except asyncio.TimeoutError:
            await response_to_user.delete()
            return
        else:
            if isinstance(event.interaction, hikari.CommandInteraction):
                await response_to_user.delete()
                return
            elif event.interaction.custom_id == "<<":
                index = 0
            elif event.interaction.custom_id == "<":
                index = (index - 1) % len(values)
            elif event.interaction.custom_id == ">":
                index = (index + 1) % len(values)
            elif event.interaction.custom_id == ">>":
                index = len(values) - 1

            await response_to_user.edit(values[index])
            await event.interaction.create_initial_response(
                hikari.interactions.base_interactions.ResponseType.DEFERRED_MESSAGE_UPDATE,
                values[index]
            )
        

# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
    client.add_component(explanation_component.copy())