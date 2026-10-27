# Copyright (c) 2022-present l3keboy

import datetime
import logging
import time
import uuid
import zoneinfo

import hikari
import lightbulb

from victreebot.contants import SUPPORTED_LANGUAGES
from victreebot.contants import SUPPORTED_LOCATION_TYPES
from victreebot.contants import SUPPORTED_RAID_TYPES
from victreebot.core.bot import Bot
from victreebot.extensions.functions.raids.commands import group
from victreebot.extensions.functions.raids.menus.time_menu import TimeModal
from victreebot.languages import en
from victreebot.models.GuildStats import Guild_StatsUpdate
from victreebot.models.Users import UsersUpdate
from victreebot.utils.classes.RaidClass import RaidClass
from victreebot.utils.shared_autocompletes import autocomplete_locations
from victreebot.utils.shared_autocompletes import autocomplete_pokemon

# Load command
loader = lightbulb.Loader()
loader.command(group)


# Functions
async def generate_check_raid_id(bot: Bot) -> str:
    """Check and generate a unique verifier ID."""
    logging.getLogger(__name__).info("Generating raid_id.....")
    # Generate a unique verifier ID
    raid_id = f"{uuid.uuid4()}"

    # Check verifier ID's in the database
    all_raid_ids = await bot.database.get_distinct_raid_id()

    # Regenerate if Ticket type ID already exists
    if raid_id in all_raid_ids:
        return await generate_check_raid_id(bot)
    # Return the unique Ticket type ID
    return raid_id


# Command
@group.register
class RaidsCreate(lightbulb.SlashCommand, name="create", description="Create a raid"):
    """Command to create a raid."""

    boss: str = lightbulb.string(
        "boss",
        "The boss to fight",
        autocomplete=autocomplete_pokemon,  # type: ignore[arg-type]  # mypy: ignore
    )
    location: str = lightbulb.string(
        "location",
        "The location the raid takes place",
        autocomplete=autocomplete_locations,  # type: ignore[arg-type]  # mypy: ignore
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
            response_message = await ctx.respond(
                language_helper.response_not_yet_setup.format(bot_name=bot.vars.BOT_NAME.capitalize())
            )
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            return

        # Validate existing raids channel ID
        if guild_settings.raids_channel_id is None:
            response_message = await ctx.respond(
                language_helper.response_raid_create_no_raids_channel.format(boss_name=self.boss),
                components=[],
                embeds=[],
            )
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_raid_create_no_raids_channel.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        # Validate emojis
        if (
            guild_settings.instinct_emoji_id is None
            or guild_settings.mystic_emoji_id is None
            or guild_settings.valor_emoji_id is None
        ):
            response_message = await ctx.respond(
                language_helper.response_raid_create_missing_emojis, components=[], embeds=[]
            )
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_raid_create_missing_emojis.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        # Validate boss
        pokemon_image: str | None = None
        if self.boss not in {"egg1", "egg3", "egg5", "eggmega", "eggshadow"}:
            success, pokemon, pokemon_image = await bot.utils.validate_pokemon(self.boss)
            if not success or not pokemon or not pokemon_image:
                response_message = await ctx.respond(
                    language_helper.response_raid_create_unknown_boss.format(boss_name=self.boss),
                    components=[],
                    embeds=[],
                )
                await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                if guild_log_settings.log_errors:
                    log_response = language_helper.log_response_raid_create_unknown_boss.format(
                        datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                    )
                    await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                return
            pokemon_name = pokemon.name
        else:
            pokemon = self.boss
            pokemon_name = self.boss
            if self.boss == "egg1":
                pokemon_image = "assets/raidEggs/raid_eggOne.png"
            elif self.boss == "egg3":
                pokemon_image = "assets/raidEggs/raid_eggThree.png"
            elif self.boss == "egg5":
                pokemon_image = "assets/raidEggs/raid_eggFive.png"
            elif self.boss == "eggmega":
                pokemon_image = "assets/raidEggs/raid_eggMega.png"
            elif self.boss == "eggshadow":
                pokemon_image = "assets/raidEggs/raid_eggShadow.png"

        if pokemon_image is None:
            return

        # Get raid type
        auto_delete_helper = max(auto_delete_helper, 120)

        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.raid_create_embed_title_raid_type),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.raid_create_embed_description_raid_type
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.InteractiveButtonBuilder(
                                style=hikari.ButtonStyle.PRIMARY,
                                label=raid_type,
                                custom_id=f"raids,{raid_type.lower()}",
                            )
                            for raid_type in SUPPORTED_RAID_TYPES
                        ]
                    ),
                ],
            )
        ]

        response_message = await ctx.respond(components=components)

        listening = True
        raid_type = ""
        while listening:
            try:
                event = await bot.wait_for(
                    hikari.ComponentInteractionCreateEvent,
                    timeout=max(auto_delete_helper, 30),
                    predicate=lambda event: event.interaction.user.id == ctx.user.id,
                )

                command, action = event.interaction.custom_id.split(",")
                if command != "raids":
                    return

                await event.interaction.create_initial_response(6)
                raid_type = action

                listening = False
            except TimeoutError:
                await ctx.delete_response(response_message)
                listening = False
            except Exception:
                logging.getLogger(__name__).exception("An error occurred while listening for the raids command!")
                await ctx.delete_response(response_message)
                listening = False

        # Validate location and location type
        location_name = ""
        location_type = ""
        location_splitted = self.location.split(",")
        if len(location_splitted) == 1:
            location_name = location_splitted[0].replace("'", "''")
            location_name = f"{location_name}"

            components = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.raid_create_embed_title_location_type
                        ),
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.raid_create_embed_description_location_type
                        ),
                        hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                        hikari.impl.MessageActionRowBuilder(
                            components=[
                                hikari.impl.InteractiveButtonBuilder(
                                    style=hikari.ButtonStyle.PRIMARY,
                                    label=location_type,
                                    custom_id=f"raids,{location_type.lower()}",
                                )
                                for location_type in SUPPORTED_LOCATION_TYPES
                            ]
                        ),
                    ],
                )
            ]
            await ctx.edit_response(response_message, components=components)

            listening = True
            while listening:
                try:
                    event = await bot.wait_for(
                        hikari.ComponentInteractionCreateEvent,
                        timeout=max(auto_delete_helper, 30),
                        predicate=lambda event: event.interaction.user.id == ctx.user.id,
                    )

                    command, action = event.interaction.custom_id.split(",")
                    if command != "raids":
                        return

                    await event.interaction.create_initial_response(6)
                    location_type = action

                    listening = False
                except TimeoutError:
                    await ctx.delete_response(response_message)
                    listening = False
                except Exception:
                    logging.getLogger(__name__).exception("An error occurred while listening for the raids command!")
                    await ctx.delete_response(response_message)
                    listening = False
        else:
            location_name = location_splitted[1].removeprefix(" ")
            location_name = location_name.replace("'", "''")
            location_type = f"{location_splitted[0]}"

        latitude = ""
        longitude = ""
        location = await bot.database.get_location(ctx.guild_id, location_type, location_name)
        if location is not None:
            latitude = location.latitude
            longitude = location.longitude

        timezone = zoneinfo.ZoneInfo(guild_settings.gmt)

        timezone_aware_current_date = datetime.datetime.today().astimezone(timezone).date()
        days = [timezone_aware_current_date + datetime.timedelta(days=offset) for offset in range(24)]

        components = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.raid_create_embed_title_date),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.raid_create_embed_description_date),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.MessageActionRowBuilder(
                        components=[
                            hikari.impl.TextSelectMenuBuilder(
                                custom_id="raids,date",
                                min_values=1,
                                max_values=1,
                                options=[
                                    hikari.impl.SelectOptionBuilder(
                                        label=(
                                            f"{language_helper.weekdays[day.weekday()]} {day.day} "
                                            f"{language_helper.months[day.month - 1]}"
                                        ),
                                        value=day.isoformat(),
                                    )
                                    for day in days[:24]
                                ],
                            )
                        ]
                    ),
                ],
            )
        ]

        await ctx.edit_response(response_message, components=components)

        listening = True
        raid_time = ""
        raid_date = ""
        while listening:
            try:
                event = await bot.wait_for(
                    hikari.ComponentInteractionCreateEvent,
                    timeout=max(auto_delete_helper, 30),
                    predicate=lambda event: event.interaction.user.id == ctx.user.id,
                )

                command, action = event.interaction.custom_id.split(",")
                if command != "raids":
                    return

                raid_date = event.interaction.values[0]

                # Time modal popup
                time_modal = TimeModal(guild_settings.language)
                await event.interaction.create_modal_response(
                    language_helper.raid_create_modal_time, "_get_raid_time", components=time_modal
                )

                try:
                    await time_modal.attach(bot.client, "_get_raid_time", timeout=auto_delete_helper)
                except TimeoutError:
                    await ctx.delete_response(response_message)
                    listening = False
                else:
                    if time_modal.selected_btn == "_get_raid_time" and (time_modal.given_time is not None):
                        raid_time = time_modal.given_time
                        valid_time = await bot.utils.validate_timestamp_format(raid_time, "%H:%M")
                        if not valid_time:
                            components_invalid_time = [
                                hikari.impl.ContainerComponentBuilder(
                                    accent_color=hikari.Colour(0x8BC683),
                                    components=[
                                        hikari.impl.TextDisplayComponentBuilder(
                                            content=language_helper.response_raid_create_invalid_time
                                        )
                                    ],
                                )
                            ]
                            await ctx.edit_response(response_message, embeds=[], components=components_invalid_time)
                            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
                            if guild_log_settings.log_errors:
                                log_response = language_helper.log_response_raid_create_invalid_time.format(
                                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                                )
                                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
                            return

                listening = False
            except TimeoutError:
                await ctx.delete_response(response_message)
                listening = False
            except Exception:
                logging.getLogger(__name__).exception("An error occurred while listening for the raids command!")
                await ctx.delete_response(response_message)
                listening = False

        raid_date = await bot.utils.change_timestamp_format(raid_date, "%Y-%m-%d", "%d/%m/%Y")
        raid_takes_place_at = f"{raid_date} {raid_time}"

        if guild_settings.extended_time_format:
            raid_takes_place_at_to_show = f"{raid_date} {raid_time} {guild_settings.gmt}"
        else:
            raid_takes_place_at_to_show = f"{raid_time}"

        raid_takes_place_at_server_timezone_aware = datetime.datetime.strptime(
            str(raid_takes_place_at), "%d/%m/%Y %H:%M"
        ).replace(tzinfo=timezone)
        datetime_obj_now_utc = datetime.datetime.now().astimezone(tz=zoneinfo.ZoneInfo("UTC"))
        datetime_obj_raid_takes_place_at_utc = raid_takes_place_at_server_timezone_aware.astimezone(
            tz=zoneinfo.ZoneInfo("UTC")
        )

        if datetime_obj_raid_takes_place_at_utc < datetime_obj_now_utc:
            components_date_passed = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(
                            content=language_helper.response_raid_create_date_time_already_past
                        )
                    ],
                )
            ]
            await ctx.edit_response(response_message, embeds=[], components=components_date_passed)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_raid_create_date_time_already_past.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        raid_id = await generate_check_raid_id(bot)

        difference = datetime_obj_raid_takes_place_at_utc - datetime_obj_now_utc
        end_time = time.time() + difference.total_seconds() + int(guild_settings.raid_timeout)

        # Create message component
        components_raid_messsage = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.SectionComponentBuilder(
                        accessory=hikari.impl.ThumbnailComponentBuilder(media=pokemon_image),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(
                                content=language_helper.raid_embed_description_with_location_link.format(
                                    raid_id=raid_id.strip("'"),
                                    raid_type=raid_type.capitalize(),
                                    time_date=f"""{raid_takes_place_at_to_show.strip("'")}""",
                                    location=location_name.capitalize()
                                    .replace("''", "'")
                                    .removeprefix("'")
                                    .removesuffix("'"),
                                    latitude=latitude,
                                    longitude=longitude,
                                )
                                if latitude is not None and latitude != ""
                                else language_helper.raid_embed_description_without_location_link.format(
                                    raid_id=raid_id.strip("'"),
                                    raid_type=raid_type.capitalize(),
                                    time_date=f"""{raid_takes_place_at_to_show.strip("'")}""",
                                    location=location_name.capitalize()
                                    .replace("''", "'")
                                    .removeprefix("'")
                                    .removesuffix("'"),
                                )
                            )
                        ],
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.raid_embed_subdescription.format(
                            instinct="\u200b", mystic="\u200b", valor="\u200b", remote="\u200b"
                        )
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(
                        content=language_helper.raid_embed_footer.format(member=ctx.user.display_name, attendees="0")
                    ),
                ],
            )
        ]

        # Send message
        raid_message = await bot.discord_service.create_message(
            guild_settings.raids_channel_id, None, components=components_raid_messsage
        )
        if raid_message is None:
            components_failed = [
                hikari.impl.ContainerComponentBuilder(
                    accent_color=hikari.Colour(0x8BC683),
                    components=[
                        hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_raid_create_failed)
                    ],
                )
            ]
            await ctx.edit_response(response_message, embeds=[], components=components_failed)
            await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
            if guild_log_settings.log_errors:
                log_response = language_helper.log_response_raid_create_failed.format(
                    datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
                )
                await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
            return

        # Add reactions
        emoji_instinct = bot.cache.get_emoji(guild_settings.instinct_emoji_id) or await bot.discord_service.get_emoji(
            ctx.guild_id, guild_settings.instinct_emoji_id
        )
        if emoji_instinct:
            await bot.discord_service.add_reaction(
                guild_settings.raids_channel_id, raid_message, emoji_instinct.name, emoji_instinct.id
            )

        emoji_mystic = bot.cache.get_emoji(guild_settings.mystic_emoji_id) or await bot.discord_service.get_emoji(
            ctx.guild_id, guild_settings.mystic_emoji_id
        )
        if emoji_mystic:
            await bot.discord_service.add_reaction(
                guild_settings.raids_channel_id, raid_message, emoji_mystic.name, emoji_mystic.id
            )

        emoji_valor = bot.cache.get_emoji(guild_settings.valor_emoji_id) or await bot.discord_service.get_emoji(
            ctx.guild_id, guild_settings.valor_emoji_id
        )
        if emoji_valor:
            await bot.discord_service.add_reaction(
                guild_settings.raids_channel_id, raid_message, emoji_valor.name, emoji_valor.id
            )

        one_emoji = "1️⃣"
        two_emoji = "2️⃣"
        three_emoji = "3️⃣"
        remote_emoji = "🇷"
        await bot.discord_service.add_reaction(guild_settings.raids_channel_id, raid_message, one_emoji)
        await bot.discord_service.add_reaction(guild_settings.raids_channel_id, raid_message, two_emoji)
        await bot.discord_service.add_reaction(guild_settings.raids_channel_id, raid_message, three_emoji)
        await bot.discord_service.add_reaction(guild_settings.raids_channel_id, raid_message, remote_emoji)

        # Create RaidClass
        RaidClass(
            raid_id,
            raid_type,
            location_type,
            location_name,
            raid_takes_place_at,
            raid_takes_place_at_to_show,
            pokemon_name.lower(),
            ctx.guild_id,
            int(end_time),
            guild_settings.raids_channel_id,
            int(raid_message),
            ctx.user.id,
            bot,
            guild_settings.language,
            guild_settings.auto_delete,
            is_new_raid=True,
        )

        # Update stats server
        new_server_stats = Guild_StatsUpdate(guild_id=ctx.guild_id, raids_created=guild_stats.raids_created + 1)
        await bot.database.change_guild_stats_settings(guild_stats, new_server_stats)

        # Update stats user
        current_user_details = await bot.database.get_user_for_guild(ctx.guild_id, ctx.user.id)
        if current_user_details:
            new_user = UsersUpdate(
                guild_id=ctx.guild_id,
                user_id=ctx.user.id,
                stats_raids_created=current_user_details.stats_raids_created + 1,
            )
            await bot.database.change_user(current_user_details, new_user)

        # Respond finished
        components_finished = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.response_raid_create_success)
                ],
            )
        ]
        await ctx.edit_response(response_message, embeds=[], components=components_finished)
        await bot.utils.handle_auto_delete(ctx.channel_id, response_message, auto_delete_helper)
        if guild_log_settings.log_raid_create:
            log_response = language_helper.log_response_raid_create_success.format(
                datetime=await bot.utils.get_timestamp_aware(guild_settings.gmt), member=ctx.member
            )
            await bot.utils.handle_log_message(bot, ctx.guild_id, log_response)
