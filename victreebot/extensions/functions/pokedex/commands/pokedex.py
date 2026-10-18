# Copyright (c) 2022-present l3keboy

import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.core.bot import Bot
from victreebot.languages import en
from victreebot.utils.shared_autocompletes import autocomplete_pokemon

# Load command
loader = lightbulb.Loader()


# Command
@loader.command
class Pokedex(lightbulb.SlashCommand, name="pokedex", description="Search details of a pokemon"):
    """Command to get info about a pokemon."""

    boss: str = lightbulb.string(
        "boss",
        "The name or ID of the Pokémon to get details off.",
        autocomplete=autocomplete_pokemon,  # type: ignore[arg-type]  # mypy: ignore
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
            response_message = await ctx.respond(
                language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize())
            )
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        try:
            int(self.boss)
            boss = int(self.boss)
        except ValueError:
            boss = self.boss.replace(" ", "-")
            boss = self.boss.lower()

        if guild_settings.unit_system == "Metric System":
            height_unit = language_helper.height_metric_system
            weight_unit = language_helper.weight_metric_system
        elif guild_settings.unit_system == "Imperial System":
            height_unit = language_helper.height_imperial_system
            weight_unit = language_helper.weight_imperial_system
        else:
            height_unit = language_helper.height_usc_system
            weight_unit = language_helper.weight_usc_system

        pokemon_image: str | None = None
        if boss not in {"egg1", "egg3", "egg5", "eggmega"}:
            success, pokemon, pokemon_image = await bot.utils.validate_pokemon(self.boss)
            if not success or not pokemon or not pokemon_image:
                response_message = await ctx.respond(
                    language_helper.response_pokedex_unknown_pokemon.format(boss_name=boss)
                )
                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_pokedex_unknown_pokemon.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return

            pokemon_name = pokemon.name
            pokemon_id = pokemon.id

            pokemon_height_decimeters = pokemon.height
            pokemon_weight_hecto_gram = pokemon.weight
            pokemon_height_meters = pokemon_height_decimeters / 10
            pokemon_weight_gram = pokemon_weight_hecto_gram * 100
            if guild_settings.unit_system == "Metric System":
                pokemon_height = round(pokemon_height_meters, 2)
                pokemon_weight = round(pokemon_weight_gram / 1000, 2)
            elif guild_settings.unit_system == "Imperial System":
                pokemon_height = round(pokemon_height_meters / 0.3048, 3)
                pokemon_weight = round(pokemon_weight_gram * 453.592, 2)
            else:
                pokemon_height = round(pokemon_height_meters * 0.0254, 2)
                pokemon_weight = round(pokemon_weight_gram * 453.592, 2)

            pokemon_abilities: list[str] = []
            pokemon_all_abilities = pokemon.abilities
            pokemon_abilities = [str(ability.ability) for ability in pokemon_all_abilities]

        else:
            pokemon_name = self.boss.capitalize()
            pokemon_id = language_helper.unknown
            pokemon_height = language_helper.unknown
            pokemon_weight = language_helper.unknown
            pokemon_abilities = [language_helper.unknown]
            if boss == "egg1":
                pokemon_image = "assets/raidEggs/raid_eggOne.png"
            elif boss == "egg3":
                pokemon_image = "assets/raidEggs/raid_eggThree.png"
            elif boss == "egg5":
                pokemon_image = "assets/raidEggs/raid_eggFive.png"
            elif boss == "eggmega":
                pokemon_image = "assets/raidEggs/raid_eggMega.png"

        if pokemon_image is None:
            return

        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.pokedex_embed_title.format(pokemon=pokemon_name.capitalize())
                    ),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.pokedex_embed_name_title),
                    hikari.impl.TextDisplayComponentBuilder(content=pokemon_name.capitalize()),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.pokedex_embed_id_title),
                    hikari.impl.TextDisplayComponentBuilder(content=str(pokemon_id)),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.pokedex_embed_length_weight_title),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=f"{pokemon_height} {height_unit}  |  {pokemon_weight} {weight_unit}"
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.pokedex_embed_abilities_title),
                    hikari.impl.TextDisplayComponentBuilder(
                        content="\n".join("- " + str(ability).capitalize() for ability in pokemon_abilities)
                    ),
                    hikari.impl.MediaGalleryComponentBuilder(
                        items=[hikari.impl.MediaGalleryItemBuilder(media=pokemon_image)]
                    ),
                ],
            )
        ]

        auto_delete_helper = max(auto_delete_helper, 20)
        response_message = await ctx.respond(components=components)
        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
        if guild_log_settings.log_info:
            log_response = language_helper.log_response_pokedex_requested.format(
                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
            )
            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
        return
