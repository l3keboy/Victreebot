# Copyright (c) 2022-present l3keboy

from io import BytesIO

import aiohttp
import hikari
import lightbulb
from PIL import Image

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.languages import en
from victreebot.utils.shared_autocompletes import autocomplete_pokemon

# Load command
loader = lightbulb.Loader()


# Command
@loader.command
class Trade(
    lightbulb.SlashCommand,
    name="trade",
    description="Create a trade offer/search/proposal (fill both options for proposal)",
):
    """Command to reset the bots settings."""

    offer: str | None = lightbulb.string(
        "offer",
        "The Pokemon you are willing to trade (leave empty for search only)",
        default=None,
        autocomplete=autocomplete_pokemon,  # type: ignore[arg-type]  # mypy: ignore
    )
    search: str | None = lightbulb.string(
        "search",
        "The Pokemon you are looking for (leave empty to offer only)",
        default=None,
        autocomplete=autocomplete_pokemon,  # type: ignore[arg-type]  # mypy: ignore
    )

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context, bot: Bot) -> None:
        """Handle command interaction."""
        await ctx.defer()
        if ctx.guild_id is None:
            await ctx.respond("Command must be executed in a server.")
            return
        member_name = ctx.member.display_name if ctx.member is not None else ctx.user.username

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

        if self.offer is None and self.search is None:
            response_message = await ctx.respond(language_helper.response_trade_insert_at_least_one)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_trade_insert_at_least_one.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        if self.offer is not None and self.search is None:
            success, pokemon_offer, pokemon_image_offer = await bot.utils.validate_pokemon(self.offer)
            if not success or not pokemon_offer or not pokemon_image_offer:
                response_message = await ctx.respond(
                    language_helper.response_trade_offer_unknown_pokemon_offer.format(boss_name=pokemon_offer)
                )
                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_trade_offer_unknown_pokemon_offer.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return

            components = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.trade_offer_embed_title),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_offer_embed_description.format(
                                pokemon_offer=pokemon_offer.name.capitalize()
                            )
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_proposal_embed_field_offering.format(
                                pokemon_offer=pokemon_offer.name.capitalize()
                            )
                        ),
                        hikari.impl.MediaGalleryComponentBuilder(
                            items=[hikari.impl.MediaGalleryItemBuilder(media=pokemon_image_offer)]
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_offered_embed_footer.format(member=member_name)
                        ),
                    ],
                )
            ]

            response_message = await ctx.respond(components=components, user_mentions=True)
            if guild_log_settings.log_trade_offer:
                log_response = language_helper.log_response_trade_offer_member_offering.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        if self.offer is None and self.search is not None:
            success, pokemon_search, pokemon_image_search = await bot.utils.validate_pokemon(self.search)
            if not success or not pokemon_search or not pokemon_image_search:
                response_message = await ctx.respond(
                    language_helper.response_trade_offer_unknown_pokemon_search.format(boss_name=pokemon_search)
                )
                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_trade_offer_unknown_pokemon_search.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return

            components = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.trade_search_embed_title),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_search_embed_description.format(
                                pokemon_search=pokemon_search.name.capitalize()
                            )
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_proposal_embed_field_search.format(
                                pokemon_search=pokemon_search.name.capitalize()
                            )
                        ),
                        hikari.impl.MediaGalleryComponentBuilder(
                            items=[hikari.impl.MediaGalleryItemBuilder(media=pokemon_image_search)]
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_search_embed_footer.format(member=member_name)
                        ),
                    ],
                )
            ]

            response_message = await ctx.respond(components=components, user_mentions=True)
            if guild_log_settings.log_trade_offer:
                log_response = language_helper.log_response_trade_search_member_searching.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        if self.offer is not None and self.search is not None:
            success, pokemon_offer, pokemon_image_offer = await bot.utils.validate_pokemon(self.offer)
            if not success or not pokemon_offer or not pokemon_image_offer:
                response_message = await ctx.respond(
                    language_helper.response_trade_offer_unknown_pokemon_offer.format(boss_name=pokemon_offer)
                )
                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_trade_offer_unknown_pokemon_offer.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return

            success, pokemon_search, pokemon_image_search = await bot.utils.validate_pokemon(self.search)
            if not success or not pokemon_search or not pokemon_image_search:
                response_message = await ctx.respond(
                    language_helper.response_trade_offer_unknown_pokemon_search.format(boss_name=pokemon_search)
                )
                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_trade_offer_unknown_pokemon_search.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return

            async with aiohttp.ClientSession() as session, session.get(pokemon_image_offer) as response:
                pokemon_image_offer = await response.read()
            async with aiohttp.ClientSession() as session, session.get(pokemon_image_search) as response:
                pokemon_image_search = await response.read()

            pokemon_image_offer = Image.open(BytesIO(pokemon_image_offer))
            pokemon_image_search = Image.open(BytesIO(pokemon_image_search))
            combined_image = Image.new(
                "RGBA", (5 * pokemon_image_offer.size[0], pokemon_image_offer.size[1]), (0, 0, 0, 0)
            )
            combined_image.paste(pokemon_image_offer, (0, 0))
            combined_image.paste(pokemon_image_search, (pokemon_image_offer.size[0], 0))

            combined_image_bytes = BytesIO()
            combined_image.save(combined_image_bytes, "PNG")
            combined_image_bytes = combined_image_bytes.getvalue()

            components = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.trade_proposal_embed_title),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_proposal_embed_description.format(
                                pokemon_search=pokemon_search.name.capitalize(),
                                pokemon_offer=pokemon_offer.name.capitalize(),
                            )
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_proposal_embed_field_offering.format(
                                pokemon_offer=pokemon_offer.name.capitalize()
                            )
                        ),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_proposal_embed_field_search.format(
                                pokemon_search=pokemon_search.name.capitalize()
                            )
                        ),
                        hikari.impl.MediaGalleryComponentBuilder(
                            items=[hikari.impl.MediaGalleryItemBuilder(media=combined_image_bytes)]
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.trade_proposal_embed_footer.format(member=member_name)
                        ),
                    ],
                )
            ]

            response_message = await ctx.respond(components=components, user_mentions=True)
            if guild_log_settings.log_trade_offer:
                log_response = language_helper.log_response_trade_proposal_member_proposing.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return
