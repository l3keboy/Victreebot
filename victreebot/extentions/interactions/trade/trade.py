# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import asyncio
import os
from io import BytesIO

import aiohttp
import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from PIL import Image
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# FUNCTIONS #
# ------------------------------------------------------------------------- #
async def get_pokemons_to_trade_proposal(
    ctx: tanjun.abc.SlashContext,
    event: hikari.InteractionCreateEvent,
    db: DatabaseHandler,
    bot: BotUtils,
    bot_aware: Bot,
) -> str:
    language, auto_delete, gmt, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt"]
    )
    log_errors, *none = await db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors"])

    timeout = 120
    pokemon_offer_name_action_row = (
        ctx.rest.build_action_row()
        .add_text_input(
            label=SUPPORTED_LANGUAGES.get(language).pokemon_offer_name_modal_text_input_title,
            custom_id="pokemon_offer_name",
        )
        .set_placeholder(SUPPORTED_LANGUAGES.get(language).pokemon_offer_modal_text_input_placeholder)
        .set_required(True)
        .add_to_container()
    )
    pokemon_search_name_action_row = (
        ctx.rest.build_action_row()
        .add_text_input(
            label=SUPPORTED_LANGUAGES.get(language).pokemon_search_modal_text_input_title,
            custom_id="pokemon_search_name",
        )
        .set_placeholder(SUPPORTED_LANGUAGES.get(language).pokemon_search_modal_text_input_placeholder)
        .set_required(True)
        .add_to_container()
    )

    await event.interaction.create_modal_response(
        SUPPORTED_LANGUAGES.get(language).boss_name_modal_trade,
        "pokemon_proposal_modal",
        components=[pokemon_offer_name_action_row, pokemon_search_name_action_row],
    )

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
            and event.interaction.user.id == ctx.author.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_trade_interactions_timeout_reached
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_interactions_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        await event.interaction.create_initial_response(6)
        if event.interaction.custom_id == "pokemon_proposal_modal":
            if (
                event.interaction.components[0][0].value is not None
                and event.interaction.components[1][0].value is not None
            ):
                pokemon_offer = event.interaction.components[0][0].value
                pokemon_search = event.interaction.components[1][0].value
                try:
                    int(pokemon_offer)
                    pokemon_offer = int(pokemon_offer)
                except Exception:
                    pokemon_offer = pokemon_offer.replace(" ", "-")
                try:
                    int(pokemon_search)
                    pokemon_search = int(pokemon_search)
                except Exception:
                    pokemon_search = pokemon_search.replace(" ", "-")

                return pokemon_offer, pokemon_search


async def get_pokemons_to_trade_offer(
    ctx: tanjun.abc.SlashContext,
    event: hikari.InteractionCreateEvent,
    db: DatabaseHandler,
    bot: BotUtils,
    bot_aware: Bot,
) -> str:
    language, auto_delete, gmt, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt"]
    )
    log_errors, *none = await db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors"])

    timeout = 120
    pokemon_offer_name_action_row = (
        ctx.rest.build_action_row()
        .add_text_input(
            label=SUPPORTED_LANGUAGES.get(language).pokemon_offer_name_modal_text_input_title,
            custom_id="pokemon_offer_name",
        )
        .set_placeholder(SUPPORTED_LANGUAGES.get(language).pokemon_offer_modal_text_input_placeholder)
        .set_required(True)
        .add_to_container()
    )

    await event.interaction.create_modal_response(
        SUPPORTED_LANGUAGES.get(language).boss_name_modal_trade,
        "pokemon_proposal_modal",
        components=[pokemon_offer_name_action_row],
    )

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
            and event.interaction.user.id == ctx.author.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_trade_interactions_timeout_reached
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_interactions_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        await event.interaction.create_initial_response(6)
        if event.interaction.custom_id == "pokemon_proposal_modal":
            if event.interaction.components[0][0].value is not None:
                pokemon_offer = event.interaction.components[0][0].value
                try:
                    int(pokemon_offer)
                    pokemon_offer = int(pokemon_offer)
                except Exception:
                    pokemon_offer = pokemon_offer.replace(" ", "-")

                return pokemon_offer


async def get_pokemons_to_trade_search(
    ctx: tanjun.abc.SlashContext,
    event: hikari.InteractionCreateEvent,
    db: DatabaseHandler,
    bot: BotUtils,
    bot_aware: Bot,
) -> str:
    language, auto_delete, gmt, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt"]
    )
    log_errors, *none = await db.get_guild_log_settings(ctx.get_guild(), settings=["log_errors"])

    timeout = 120
    pokemon_search_name_action_row = (
        ctx.rest.build_action_row()
        .add_text_input(
            label=SUPPORTED_LANGUAGES.get(language).pokemon_search_modal_text_input_title,
            custom_id="pokemon_search_name",
        )
        .set_placeholder(SUPPORTED_LANGUAGES.get(language).pokemon_search_modal_text_input_placeholder)
        .set_required(True)
        .add_to_container()
    )

    await event.interaction.create_modal_response(
        SUPPORTED_LANGUAGES.get(language).boss_name_modal_trade,
        "pokemon_proposal_modal",
        components=[pokemon_search_name_action_row],
    )

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ModalInteraction)
            and event.interaction.user.id == ctx.author.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_trade_interactions_timeout_reached
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_interactions_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        await event.interaction.create_initial_response(6)
        if event.interaction.custom_id == "pokemon_proposal_modal":
            if event.interaction.components[0][0].value is not None:
                pokemon_search = event.interaction.components[0][0].value
                try:
                    int(pokemon_search)
                    pokemon_search = int(pokemon_search)
                except Exception:
                    pokemon_search = pokemon_search.replace(" ", "-")

                return pokemon_search


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.as_slash_command("trade", "Interacions for trading")
async def command_trade(
    ctx: tanjun.abc.SlashContext,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    language, auto_delete, gmt, is_setup, *none = await db.get_guild_settings(
        guild=ctx.get_guild(), settings=["language", "auto_delete", "gmt", "is_setup"]
    )
    log_errors, log_trade_proposal, log_trade_offer, log_trade_search, *none = await db.get_guild_log_settings(
        ctx.get_guild(), settings=["log_errors", "log_trade_proposal", "log_trade_offer", "log_trade_search"]
    )

    if not is_setup:
        response = SUPPORTED_LANGUAGES.get(language).response_not_yet_setup.format(bot_name=BOT_NAME.capitalize())
        await ctx.edit_last_response(response, delete_after=auto_delete)
        return

    timeout = 120
    embed = hikari.Embed(
        title=SUPPORTED_LANGUAGES.get(language).trade_embed_title,
        description=SUPPORTED_LANGUAGES.get(language).trade_embed_description,
        colour=hikari.Colour(0x8BC683),
    )

    action_row_1 = (
        ctx.rest.build_action_row()
        .add_button(hikari.ButtonStyle.PRIMARY, "proposal")
        .set_label(SUPPORTED_LANGUAGES.get(language).trade_action_row_proposal)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "offer")
        .set_label(SUPPORTED_LANGUAGES.get(language).trade_action_row_offer)
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "search")
        .set_label(SUPPORTED_LANGUAGES.get(language).trade_action_row_search)
        .add_to_container()
    )

    response_message = await ctx.respond(embed, components=[action_row_1])

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent,
            timeout=timeout,
            predicate=lambda event: isinstance(event.interaction, hikari.ComponentInteraction)
            and event.interaction.user.id == ctx.author.id
            and event.interaction.message.id == response_message.id,
        )
    except asyncio.TimeoutError:
        response = SUPPORTED_LANGUAGES.get(language).response_trade_interactions_timeout_reached
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_interactions_timeout_reached.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return
    else:
        if event.interaction.custom_id == "proposal":
            pokemon_offer, pokemon_search = await get_pokemons_to_trade_proposal(ctx, event, db, bot, bot_aware)
            success, pokemon_offer, pokemon_image_offer = await bot.validate_pokemon(pokemon_offer)
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_trade_offer_unknown_pokemon_offer.format(
                    boss_name=pokemon_offer
                )
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_trade_offer_unknown_pokemon_offer.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            success, pokemon_search, pokemon_image_search = await bot.validate_pokemon(pokemon_search)
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_trade_offer_unknown_pokemon_search.format(
                    boss_name=pokemon_search
                )
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_trade_offer_unknown_pokemon_search.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            async with aiohttp.ClientSession() as session:
                async with session.get(pokemon_image_offer) as response:
                    pokemon_image_offer = await response.read()
            async with aiohttp.ClientSession() as session:
                async with session.get(pokemon_image_search) as response:
                    pokemon_image_search = await response.read()

            pokemon_image_offer = Image.open(BytesIO(pokemon_image_offer))
            pokemon_image_search = Image.open(BytesIO(pokemon_image_search))
            combined_image = Image.new(
                "RGBA", (5 * pokemon_image_offer.size[0], pokemon_image_offer.size[1]), (0, 0, 0, 0)
            )
            combined_image.paste(pokemon_image_offer, (0, 0))
            combined_image.paste(pokemon_image_search, (pokemon_image_offer.size[0] + 200, 0))

            combined_image_bytes = BytesIO()
            combined_image.save(combined_image_bytes, "PNG")
            combined_image_bytes = combined_image_bytes.getvalue()

            embed = (
                hikari.Embed(
                    title=SUPPORTED_LANGUAGES.get(language).trade_proposal_embed_title,
                    description=SUPPORTED_LANGUAGES.get(language).trade_proposal_embed_description.format(
                        pokemon_search=pokemon_search.name.capitalize(), pokemon_offer=pokemon_offer.name.capitalize()
                    ),
                    colour=hikari.Colour(0x8BC683),
                )
                .set_footer(
                    SUPPORTED_LANGUAGES.get(language).trade_proposal_embed_footer.format(member=ctx.member.display_name)
                )
                .add_field(
                    name=SUPPORTED_LANGUAGES.get(language).trade_proposal_embed_field_offering,
                    value=f"{pokemon_offer.name.capitalize()}",
                    inline=True,
                )
                .add_field(name="<->", value="\u200b", inline=True)
                .add_field(
                    name=SUPPORTED_LANGUAGES.get(language).trade_proposal_embed_field_search,
                    value=f"{pokemon_search.name.capitalize()}",
                    inline=True,
                )
                .set_image(combined_image_bytes)
            )

            await ctx.respond(
                SUPPORTED_LANGUAGES.get(language).response_trade_proposal_member_proposing.format(
                    member=ctx.member.mention
                ),
                embed=embed,
                user_mentions=True,
            )
            if log_trade_proposal:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_proposal_member_proposing.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                )
                await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "offer":
            pokemon_offer = await get_pokemons_to_trade_offer(ctx, event, db, bot, bot_aware)
            success, pokemon_offer, pokemon_image_offer = await bot.validate_pokemon(pokemon_offer)
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_trade_offer_unknown_pokemon_offer.format(
                    boss_name=pokemon_offer
                )
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_trade_offer_unknown_pokemon_offer.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            embed = (
                hikari.Embed(
                    title=SUPPORTED_LANGUAGES.get(language).trade_offer_embed_title,
                    description=SUPPORTED_LANGUAGES.get(language).trade_offer_embed_description.format(
                        pokemon_offer=pokemon_offer.name.capitalize()
                    ),
                    colour=hikari.Colour(0x8BC683),
                )
                .set_footer(
                    SUPPORTED_LANGUAGES.get(language).trade_offered_embed_footer.format(member=ctx.member.display_name)
                )
                .add_field(
                    name=SUPPORTED_LANGUAGES.get(language).trade_proposal_embed_field_offering,
                    value=f"{pokemon_offer.name.capitalize()}",
                    inline=True,
                )
                .set_image(pokemon_image_offer)
            )
            await ctx.respond(
                SUPPORTED_LANGUAGES.get(language).response_trade_offer_member_offering.format(
                    member=ctx.member.mention
                ),
                embed=embed,
                user_mentions=True,
            )
            if log_trade_offer:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_offer_member_offering.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                )
                await bot.log_from_ctx(ctx, db, log_response)

        elif event.interaction.custom_id == "search":
            pokemon_search = await get_pokemons_to_trade_search(ctx, event, db, bot, bot_aware)
            success, pokemon_search, pokemon_image_search = await bot.validate_pokemon(pokemon_search)
            if not success:
                response = SUPPORTED_LANGUAGES.get(language).response_trade_offer_unknown_pokemon_search.format(
                    boss_name=pokemon_offer
                )
                await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
                if log_errors:
                    log_response = SUPPORTED_LANGUAGES.get(
                        language
                    ).log_response_trade_offer_unknown_pokemon_search.format(
                        datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                    )
                    await bot.log_from_ctx(ctx, db, log_response)
                return

            embed = (
                hikari.Embed(
                    title=SUPPORTED_LANGUAGES.get(language).trade_search_embed_title,
                    description=SUPPORTED_LANGUAGES.get(language).trade_search_embed_description.format(
                        pokemon_search=pokemon_search.name.capitalize()
                    ),
                    colour=hikari.Colour(0x8BC683),
                )
                .set_footer(
                    SUPPORTED_LANGUAGES.get(language).trade_search_embed_footer.format(member=ctx.member.display_name)
                )
                .add_field(
                    name=SUPPORTED_LANGUAGES.get(language).trade_proposal_embed_field_search,
                    value=f"{pokemon_search.name.capitalize()}",
                    inline=True,
                )
                .set_image(pokemon_image_search)
            )
            await ctx.respond(
                SUPPORTED_LANGUAGES.get(language).response_trade_search_member_searching.format(
                    member=ctx.member.mention
                ),
                embed=embed,
                user_mentions=True,
            )
            if log_trade_search:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_search_member_searching.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                )
                await bot.log_from_ctx(ctx, db, log_response)
