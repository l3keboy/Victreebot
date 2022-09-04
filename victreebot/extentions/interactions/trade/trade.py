# IMPORTS
import os
from io import BytesIO

import aiohttp
import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from PIL import Image
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.autocomplete_callbacks import autocomplete_pokemon
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# COMMANDS #
# ------------------------------------------------------------------------- #
@tanjun.with_str_slash_option(
    "offer",
    "The Pokemon you are willing to trade (leave empty for search only)",
    default=None,
    autocomplete=autocomplete_pokemon,
)
@tanjun.with_str_slash_option(
    "search",
    "The Pokemon you are looking for (leave empty for offer only)",
    default=None,
    autocomplete=autocomplete_pokemon,
)
@tanjun.as_slash_command(
    "trade", "Create a trade offer/search/proposal (fill both options for proposal)", always_defer=True
)
async def command_trade(
    ctx: tanjun.abc.SlashContext,
    search: str,
    offer: str,
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

    if offer is None and search is None:
        response = SUPPORTED_LANGUAGES.get(language).response_trade_insert_at_least_one
        await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
        if log_errors:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_insert_at_least_one.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
        return

    if offer is not None and search is None:
        success, pokemon_offer, pokemon_image_offer = await bot.validate_pokemon(offer)
        if not success:
            response = SUPPORTED_LANGUAGES.get(language).response_trade_offer_unknown_pokemon_offer.format(
                boss_name=pokemon_offer
            )
            await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
            if log_errors:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_offer_unknown_pokemon_offer.format(
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
            SUPPORTED_LANGUAGES.get(language).response_trade_offer_member_offering.format(member=ctx.member.mention),
            embed=embed,
            user_mentions=True,
        )
        if log_trade_offer:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_offer_member_offering.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
    elif offer is None and search is not None:
        success, pokemon_search, pokemon_image_search = await bot.validate_pokemon(search)
        if not success:
            response = SUPPORTED_LANGUAGES.get(language).response_trade_offer_unknown_pokemon_search.format(
                boss_name=pokemon_offer
            )
            await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
            if log_errors:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_offer_unknown_pokemon_search.format(
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
            SUPPORTED_LANGUAGES.get(language).response_trade_search_member_searching.format(member=ctx.member.mention),
            embed=embed,
            user_mentions=True,
        )
        if log_trade_search:
            log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_search_member_searching.format(
                datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
            )
            await bot.log_from_ctx(ctx, db, log_response)
    elif offer is not None and search is not None:
        success, pokemon_offer, pokemon_image_offer = await bot.validate_pokemon(offer)
        if not success:
            response = SUPPORTED_LANGUAGES.get(language).response_trade_offer_unknown_pokemon_offer.format(
                boss_name=pokemon_offer
            )
            await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
            if log_errors:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_offer_unknown_pokemon_offer.format(
                    datetime=await bot.get_timestamp_aware(gmt), member=ctx.member
                )
                await bot.log_from_ctx(ctx, db, log_response)
            return

        success, pokemon_search, pokemon_image_search = await bot.validate_pokemon(search)
        if not success:
            response = SUPPORTED_LANGUAGES.get(language).response_trade_offer_unknown_pokemon_search.format(
                boss_name=pokemon_search
            )
            await ctx.edit_last_response(response, delete_after=auto_delete, embed=None, components=None)
            if log_errors:
                log_response = SUPPORTED_LANGUAGES.get(language).log_response_trade_offer_unknown_pokemon_search.format(
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
        combined_image = Image.new("RGBA", (5 * pokemon_image_offer.size[0], pokemon_image_offer.size[1]), (0, 0, 0, 0))
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
