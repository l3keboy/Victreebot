from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from typing import TYPE_CHECKING
import hikari

from victreebot.languages import en
from victreebot.models.GuildStats import Guild_StatsUpdate
if TYPE_CHECKING:
    from victreebot.core.bot import Bot
from dotenv import load_dotenv
from victreebot.contants import SUPPORTED_LANGUAGES

from victreebot.models.Raids import RaidsUpdate

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# CLASS #
# ------------------------------------------------------------------------- #
@dataclass
class RaidClass:
    raid_id: str
    raid_type: str
    location_type: str
    location_name: str
    takes_place_at: str
    takes_place_at_to_show: str
    boss: str
    guild_id: hikari.Snowflake | int
    end_time: int
    raid_message_channel_id: int
    raid_message_id: int
    raid_creator_id: int
    bot: Bot
    language: str
    auto_delete: int | None
    instinct_present: list[hikari.Snowflake | int] | None = None
    mystic_present: list[hikari.Snowflake | int] | None = None
    valor_present: list[hikari.Snowflake | int] | None = None
    remote_present: list[hikari.Snowflake | int] | None = None
    total_attendess: int = 0
    is_new_raid: bool = False
    task: asyncio.Future[None] = field(init=False)

    def __post_init__(self) -> None:
        self.instinct_present = self.instinct_present if self.instinct_present is not None else []
        self.mystic_present = self.mystic_present if self.mystic_present is not None else []
        self.valor_present = self.valor_present if self.valor_present is not None else []
        self.remote_present = self.remote_present if self.remote_present is not None else []

        self.wait_duration = 1 if self.end_time - time.time() <= 0 else self.end_time - time.time()
        self.task = asyncio.ensure_future(self.end_raid(self.is_new_raid))
        self.bot.raids[self.raid_id] = self

    async def end_raid(self, is_new_raid: bool) -> None:
        if is_new_raid:
            await self.bot.database.insert_raid(
                self.guild_id,
                self.raid_id, 
                self.raid_type, 
                self.location_type, 
                self.location_name, 
                str(self.takes_place_at), 
                self.boss, 
                self.end_time, 
                self.raid_message_channel_id, 
                self.raid_message_id, 
                self.raid_creator_id, 
                self.takes_place_at_to_show
            )

        await asyncio.sleep(self.wait_duration)

        guild_stats = await self.bot.database.get_guild_stats(self.guild_id)
        if guild_stats:
            new_guild_stats = Guild_StatsUpdate(guild_id=self.guild_id, raids_completed=int(guild_stats.raids_completed) + 1)
            await self.bot.database.change_guild_stats_settings(guild_stats, new_guild_stats)

        # NOTE UPDATE USER STATS!

        await self.delete_raid()

    async def update_raid_from_reaction(self, reaction: str, add: bool, member: hikari.Member) -> None:
        if reaction == "instinct" and self.instinct_present is not None:
            self.instinct_present.append(member.id) if add else self.instinct_present.remove(member.id)
        elif reaction == "mystic" and self.mystic_present is not None:
            self.mystic_present.append(member.id) if add else self.mystic_present.remove(member.id)
        elif reaction == "valor" and self.valor_present is not None:
            self.valor_present.append(member.id) if add else self.valor_present.remove(member.id)
        elif reaction == "remote" and self.remote_present is not None:
            self.remote_present.append(member.id) if add else self.remote_present.remove(member.id)

        latitude = ""
        longitude = ""
        results = await self.bot.database.get_location(self.guild_id, self.location_type, self.location_name)
        if results is not None:
            latitude = results.latitude
            longitude = results.longitude
        self.location_name = self.location_name

        if (
            reaction == "instinct"
            or reaction == "mystic"
            or reaction == "valor"
            or reaction == "remote"
            or reaction == "one"
        ):
            self.total_attendess = self.total_attendess + 1 if add else self.total_attendess - 1
        elif reaction == "two":
            self.total_attendess = self.total_attendess + 2 if add else self.total_attendess - 2
        elif reaction == "three":
            self.total_attendess = self.total_attendess + 3 if add else self.total_attendess - 3

        raid_creator = self.bot.cache.get_member(
            self.guild_id, self.raid_creator_id
        ) or await self.bot.rest.fetch_member(self.guild_id, self.raid_creator_id)

        if (
            self.boss.strip("'") != "egg1"
            and self.boss.strip("'") != "egg3"
            and self.boss.strip("'") != "egg5"
            and self.boss.strip("'") != "eggmega"
        ):
            success, pokemon, pokemon_image = await self.bot.utils.validate_pokemon(self.boss.strip("'"))
        else:
            path = Path().cwd()
            if self.boss.strip("'") == "egg1":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggOne.png"
            elif self.boss.strip("'") == "egg3":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggThree.png"
            elif self.boss.strip("'") == "egg5":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggFive.png"
            elif self.boss.strip("'") == "eggmega":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggMega.png"

        instinct_members = (
            [
                self.bot.cache.get_member(self.guild_id, instinct)
                or await self.bot.rest.fetch_member(self.guild_id, instinct)
                for instinct in self.instinct_present
            ]
            if self.instinct_present is not None and len(self.instinct_present) > 0
            else []
        )
        mystic_members = (
            [
                self.bot.cache.get_member(self.guild_id, mystic)
                or await self.bot.rest.fetch_member(self.guild_id, mystic)
                for mystic in self.mystic_present
            ]
            if self.mystic_present is not None and len(self.mystic_present) > 0
            else []
        )
        valor_members = (
            [
                self.bot.cache.get_member(self.guild_id, valor)
                or await self.bot.rest.fetch_member(self.guild_id, valor)
                for valor in self.valor_present
            ]
            if self.valor_present is not None and len(self.valor_present) > 0
            else []
        )
        remote_members = (
            [
                self.bot.cache.get_member(self.guild_id, remote)
                or await self.bot.rest.fetch_member(self.guild_id, remote)
                for remote in self.remote_present
            ]
            if self.remote_present is not None and len(self.remote_present) > 0
            else []
        )

        guild_settings = await self.bot.database.get_guild_settings(self.guild_id)
        if guild_settings is None:
            return
        
        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)

        components_raid_messsage = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.SectionComponentBuilder(
                        accessory=hikari.impl.ThumbnailComponentBuilder(
                            media=pokemon_image,
                        ),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(content=
                                language_helper.raid_embed_description_with_location_link.format(
                                    raid_id=self.raid_id.strip("'"),
                                    raid_type=self.raid_type.capitalize(),
                                    time_date=f"""{self.takes_place_at_to_show.strip("'")}""",
                                    location=self.location_name.capitalize().replace("''", "'").removeprefix("'").removesuffix("'"),
                                    latitude=latitude,
                                    longitude=longitude,
                                )
                                if latitude is not None and latitude != ""
                                else language_helper.raid_embed_description_without_location_link.format(
                                    raid_id=self.raid_id.strip("'"),
                                    raid_type=self.raid_type.capitalize(),
                                    time_date=f"""{self.takes_place_at_to_show.strip("'")}""",
                                    location=self.location_name.capitalize().replace("''", "'").removeprefix("'").removesuffix("'"),
                                )
                            ),
                        ]
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.raid_embed_subdescription.format(instinct=", ".join(instinct.display_name for instinct in instinct_members), mystic=", ".join(mystic.display_name for mystic in mystic_members), valor=", ".join(valor.display_name for valor in valor_members), remote=", ".join(remote.display_name for remote in remote_members))),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.raid_embed_footer.format(
                        member=raid_creator.display_name, attendees="0"
                    )),
                ]
            )
        ]

        raid_message = self.bot.cache.get_message(
            self.raid_message_id
        ) or await self.bot.rest.fetch_message(self.raid_message_channel_id, self.raid_message_id)
        await raid_message.edit(components=components_raid_messsage)

    async def update_raid(
        self,
        new_type: str | None = None,
        new_boss: str | None = None,
        new_location: str | None = None,
        new_location_type: str | None = None,
        new_end_time: int | None = None,
        new_raid_takes_place_at_to_show: str | None = None,
        new_raid_takes_place_at: str | None = None,
    ) -> bool:
        raid = await self.bot.database.get_raid(self.guild_id, self.raid_id)
        if raid is None:
            return False

        guild_settings = await self.bot.database.get_guild_settings(self.guild_id)
        if guild_settings is None:
            return False
        
        language_helper = SUPPORTED_LANGUAGES.get(guild_settings.language, en)

        new_raid = RaidsUpdate(
            guild_id=self.guild_id,
            raid_id=self.raid_id
        )
        if new_type is not None:
            self.raid_type = new_type
            new_raid.raid_type = new_type
        if new_boss is not None:
            self.boss = new_boss
            new_raid.boss = new_boss
        if new_location is not None:
            self.location_name = new_location
            new_raid.location_name = new_location
            new_raid.location_type = new_location_type
        if (
            new_end_time is not None
            and new_raid_takes_place_at_to_show is not None
            and new_raid_takes_place_at is not None
        ):
            self.task.cancel()
            self.takes_place_at = new_raid_takes_place_at
            self.takes_place_at_to_show = new_raid_takes_place_at_to_show
            self.end_time = new_end_time
            self.wait_duration = 1 if self.end_time - time.time() <= 0 else self.end_time - time.time()
            self.task = asyncio.ensure_future(self.end_raid(False))
            new_raid.takes_place_at = str(new_raid_takes_place_at)
            new_raid.end_time = new_end_time
            new_raid.takes_place_at_to_show = new_raid_takes_place_at_to_show

        if new_type is not None or new_boss is not None or new_location is not None or new_end_time is not None:
            raid = await self.bot.database.change_raid(raid, new_raid)
            if not raid:
                return False

        latitude = ""
        longitude = ""
        results = await self.bot.database.get_location(self.guild_id, self.location_type, self.location_name)
        if results is not None:
            latitude = results.latitude
            longitude = results.longitude

        if (
            self.boss.strip("'") != "egg1"
            and self.boss.strip("'") != "egg3"
            and self.boss.strip("'") != "egg5"
            and self.boss.strip("'") != "eggmega"
        ):
            success, pokemon, pokemon_image = await self.bot.utils.validate_pokemon(self.boss.strip("'"))
        else:
            path = Path().cwd()
            if self.boss.strip("'") == "egg1":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggOne.png"
            elif self.boss.strip("'") == "egg3":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggThree.png"
            elif self.boss.strip("'") == "egg5":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggFive.png"
            elif self.boss.strip("'") == "eggmega":
                pokemon_image = f"{path}/assets/raidEggs/raid_eggMega.png"

        raid_creator = self.bot.cache.get_member(
            self.guild_id, self.raid_creator_id
        ) or await self.bot.rest.fetch_member(self.guild_id, self.raid_creator_id)

        instinct_members = (
            [
                self.bot.cache.get_member(self.guild_id, instinct)
                or await self.bot.rest.fetch_member(self.guild_id, instinct)
                for instinct in self.instinct_present
            ]
            if self.instinct_present is not None and len(self.instinct_present) > 0
            else []
        )
        mystic_members = (
            [
                self.bot.cache.get_member(self.guild_id, mystic)
                or await self.bot.rest.fetch_member(self.guild_id, mystic)
                for mystic in self.mystic_present
            ]
            if self.mystic_present is not None and len(self.mystic_present) > 0
            else []
        )
        valor_members = (
            [
                self.bot.cache.get_member(self.guild_id, valor)
                or await self.bot.rest.fetch_member(self.guild_id, valor)
                for valor in self.valor_present
            ]
            if self.valor_present is not None and len(self.valor_present) > 0
            else []
        )
        remote_members = (
            [
                self.bot.cache.get_member(self.guild_id, remote)
                or await self.bot.rest.fetch_member(self.guild_id, remote)
                for remote in self.remote_present
            ]
            if self.remote_present is not None and len(self.remote_present) > 0
            else []
        )

        components_raid_messsage = [
            hikari.impl.ContainerComponentBuilder(
                accent_color=hikari.Colour(0x8BC683),
                components=[
                    hikari.impl.SectionComponentBuilder(
                        accessory=hikari.impl.ThumbnailComponentBuilder(
                            media=pokemon_image,
                        ),
                        components=[
                            hikari.impl.TextDisplayComponentBuilder(content=
                                language_helper.raid_embed_description_with_location_link.format(
                                    raid_id=self.raid_id.strip("'"),
                                    raid_type=self.raid_type.capitalize(),
                                    time_date=f"""{self.takes_place_at_to_show.strip("'")}""",
                                    location=self.location_name.capitalize().replace("''", "'").removeprefix("'").removesuffix("'"),
                                    latitude=latitude,
                                    longitude=longitude,
                                )
                                if latitude is not None and latitude != ""
                                else language_helper.raid_embed_description_without_location_link.format(
                                    raid_id=self.raid_id.strip("'"),
                                    raid_type=self.raid_type.capitalize(),
                                    time_date=f"""{self.takes_place_at_to_show.strip("'")}""",
                                    location=self.location_name.capitalize().replace("''", "'").removeprefix("'").removesuffix("'"),
                                )
                            ),
                        ]
                    ),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.raid_embed_subdescription.format(instinct=", ".join(instinct.display_name for instinct in instinct_members), mystic=", ".join(mystic.display_name for mystic in mystic_members), valor=", ".join(valor.display_name for valor in valor_members), remote=", ".join(remote.display_name for remote in remote_members))),
                    hikari.impl.SeparatorComponentBuilder(divider=True, spacing=hikari.SpacingType.LARGE),
                    hikari.impl.TextDisplayComponentBuilder(content=language_helper.raid_embed_footer.format(
                        member=raid_creator.display_name, attendees="0"
                    )),
                ]
            )
        ]

        raid_message = self.bot.cache.get_message(
            self.raid_message_id
        ) or await self.bot.rest.fetch_message(self.raid_message_channel_id, self.raid_message_id)
        await raid_message.edit(components=components_raid_messsage, attachment=None)
        return True

    async def delete_raid(self) -> None:
        raid = await self.bot.database.get_raid(self.guild_id, self.raid_id)
        if raid:
            await self.bot.database.delete_raid(raid)
            try:
                raid_message = await self.bot.rest.fetch_message(self.raid_message_channel_id, self.raid_message_id)
                await raid_message.delete()
            except hikari.NotFoundError:
                return
            except Exception as e:
                logging.getLogger(__name__).error(
                    "Unexpected error while trying to delete raid for " f"guild_id: {self.guild_id}! Got error: {e}!"
                )
            self.task.cancel()
