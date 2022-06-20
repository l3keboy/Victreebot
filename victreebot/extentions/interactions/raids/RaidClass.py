# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
import asyncio
import datetime
import os
import time
from dataclasses import dataclass
from dataclasses import field
import logging

import hikari
from core.bot import Bot
from dotenv import load_dotenv
from utils.helpers.BotUtils import BotUtils
from utils.helpers.contants import SUPPORTED_LANGUAGES

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
    takes_place_at: datetime.datetime
    boss: str
    guild: hikari.Guild
    end_time: int
    raid_message_channel_id: int
    raid_message_id: int
    raid_creator_id: int
    bot: BotUtils
    bot_aware: Bot
    language: str
    auto_delete: int
    instinct_present: list = None
    mystic_present: list = None
    valor_present: list = None
    remote_present: list = None
    total_attendess: list = 0
    task: asyncio.Future = field(init=False)

    def __post_init__(self) -> None:
        self.instinct_present = self.instinct_present if self.instinct_present is not None else []
        self.mystic_present = self.mystic_present if self.mystic_present is not None else []
        self.valor_present = self.valor_present if self.valor_present is not None else []
        self.remote_present = self.remote_present if self.remote_present is not None else []

        self.wait_duration = 1 if self.end_time - time.time() <= 0 else self.end_time - time.time()
        self.task = asyncio.ensure_future(self.end_raid())
        self.bot_aware.raids[self.raid_id] = self

    async def end_raid(self) -> None:
        self.raid_type = f"'{self.raid_type}'"
        self.takes_place_at = f"'{self.takes_place_at}'"
        self.boss = f"'{self.boss}'"
        await self.bot_aware.db.insert_raid(self.guild, self.raid_id, self.raid_type, self.location_type, self.location_name, self.takes_place_at, self.boss, self.end_time, self.raid_message_channel_id, self.raid_message_id, self.raid_creator_id)
        
        await asyncio.sleep(self.wait_duration)
        
        raids_completed, *none = await self.bot_aware.db.get_guild_stats(self.guild, stats=["raids_completed"])
        new_raids_completed = int(raids_completed) + 1
        await self.bot_aware.db.set_guild_stats(self.guild, parameters=[f"raids_completed = {new_raids_completed}"])

        # NOTE UPDATE USER STATS!

        await self.delete_raid()

    async def update_raid_from_reaction(self, reaction: str, add: bool, member: hikari.Member) -> None:
        if reaction == "instinct":
            self.instinct_present.append(member.id) if add else self.instinct_present.remove(member.id)      
        elif reaction == "mystic":
            self.mystic_present.append(member.id) if add else self.mystic_present.remove(member.id)      
        elif reaction == "valor":
            self.valor_present.append(member.id) if add else self.valor_present.remove(member.id)
        elif reaction == "remote":
            self.remote_present.append(member.id) if add else self.remote_present.remove(member.id)   

        gmt, *none = await self.bot_aware.db.get_guild_settings(
            guild=self.guild, settings=["gmt"]
        )

        results = await self.bot_aware.db.get_location_info(self.guild, self.location_type, self.location_name)
        latitude = results[0].get("latitude")
        longitude = results[0].get("longitude")
        location_name = results[0].get("name")
        
        if reaction == "instinct" or reaction == "mystic" or reaction == "valor" or reaction == "remote" or reaction == "one":
            self.total_attendess = self.total_attendess + 1 if add else self.total_attendess - 1
        elif reaction == "two":
            self.total_attendess = self.total_attendess + 2 if add else self.total_attendess - 2
        elif reaction == "three":
            self.total_attendess = self.total_attendess + 3 if add else self.total_attendess - 3
        
        raid_creator = self.bot_aware.cache.get_member(self.guild, self.raid_creator_id) or await self.bot_aware.rest.fetch_member(self.guild, self.raid_creator_id)
        
        success, pokemon, pokemon_image = await self.bot.validate_pokemon(self.boss.strip("'"))

        instinct_members = [self.bot_aware.cache.get_member(self.guild, instinct).display_name or await self.bot_aware.rest.fetch_member(self.guild, instinct).display_name for instinct in self.instinct_present] if self.instinct_present != [] else ["\u200b"]
        mystic_members = [self.bot_aware.cache.get_member(self.guild, mystic).display_name or await self.bot_aware.rest.fetch_member(self.guild, mystic).display_name for mystic in self.mystic_present] if self.mystic_present != [] else ["\u200b"]
        valor_members = [self.bot_aware.cache.get_member(self.guild, valor).display_name or await self.bot_aware.rest.fetch_member(self.guild, valor).display_name for valor in self.valor_present] if self.valor_present != [] else ["\u200b"]
        remote_members = [self.bot_aware.cache.get_member(self.guild, remote).display_name or await self.bot_aware.rest.fetch_member(self.guild, remote).display_name for remote in self.remote_present] if self.remote_present != [] else ["\u200b"]

        embed = (
            hikari.Embed(
                description=SUPPORTED_LANGUAGES.get(self.language).raid_embed_description_with_location_link.format(
                    raid_id=self.raid_id.strip("'"),
                    raid_type=self.raid_type.strip("'").capitalize(),
                    time_date=f"""{str(self.takes_place_at).strip("'")} {gmt}""",
                    location=location_name.capitalize(),
                    latitude=latitude,
                    longitude=longitude,
                ) if latitude is not None else SUPPORTED_LANGUAGES.get(self.language).raid_embed_description_without_location_link.format(
                    raid_id=self.raid_id.strip("'"),
                    raid_type=self.raid_type.strip("'").capitalize(),
                    time_date=f"""{str(self.takes_place_at).strip("'")} {gmt}""",
                    location=location_name.capitalize(),
                ),
                colour=hikari.Colour(0x8bc683),
            )
            .set_author(name=self.boss.strip("'").replace("-", " ").capitalize(), icon=pokemon_image)
            .set_footer(text=SUPPORTED_LANGUAGES.get(self.language).raid_embed_footer.format(member=raid_creator.display_name, attendees=self.total_attendess))
            .add_field("Instinct:", value=", ".join(instinct for instinct in instinct_members), inline=False)
            .add_field("Mystic:", value=", ".join(mystic for mystic in mystic_members), inline=False)
            .add_field("Valor:", value=", ".join(valor for valor in valor_members), inline=False)
            .add_field("Remote:", value=", ".join(remote for remote in remote_members), inline=False)
        )

        raid_message = self.bot_aware.cache.get_message(self.raid_message_id) or await self.bot_aware.rest.fetch_message(self.raid_message_channel_id, self.raid_message_id)
        await raid_message.edit(embed=embed)

    async def update_raid(self, new_type: str = None, new_boss: str = None, new_location: str = None, new_location_type: str = None) -> bool:
        parameters = []
        if new_type is not None:
            parameters.append(f"raid_type = '{new_type}'")
            self.raid_type = new_type
        if new_boss is not None:
            parameters.append(f"boss = '{new_boss}'")
            self.boss = new_boss
        if new_location is not None:
            parameters.append(f"location_name = {new_location}")
            parameters.append(f"location_type = {new_location_type}")
            self.location_name = new_location
        
        if new_type is not None or new_boss is not None or new_location is not None:
            success = await self.bot_aware.db.set_raid_detail(self.guild, self.raid_id, parameters=parameters)
            if not success:
                return False

        gmt, *none = await self.bot_aware.db.get_guild_settings(
            guild=self.guild, settings=["gmt"]
        )

        results = await self.bot_aware.db.get_location_info(self.guild, self.location_type, self.location_name)
        latitude = results[0].get("latitude")
        longitude = results[0].get("longitude")
        location_name = results[0].get("name")

        success, pokemon, pokemon_image = await self.bot.validate_pokemon(self.boss.strip("'"))
        
        raid_creator = self.bot_aware.cache.get_member(self.guild, self.raid_creator_id) or await self.bot_aware.rest.fetch_member(self.guild, self.raid_creator_id)

        instinct_members = [self.bot_aware.cache.get_member(self.guild, instinct).display_name or await self.bot_aware.rest.fetch_member(self.guild, instinct).display_name for instinct in self.instinct_present] if self.instinct_present != [] else ["\u200b"]
        mystic_members = [self.bot_aware.cache.get_member(self.guild, mystic).display_name or await self.bot_aware.rest.fetch_member(self.guild, mystic).display_name for mystic in self.mystic_present] if self.mystic_present != [] else ["\u200b"]
        valor_members = [self.bot_aware.cache.get_member(self.guild, valor).display_name or await self.bot_aware.rest.fetch_member(self.guild, valor).display_name for valor in self.valor_present] if self.valor_present != [] else ["\u200b"]
        remote_members = [self.bot_aware.cache.get_member(self.guild, remote).display_name or await self.bot_aware.rest.fetch_member(self.guild, remote).display_name for remote in self.remote_present] if self.remote_present != [] else ["\u200b"]

        embed = (
            hikari.Embed(
                description=SUPPORTED_LANGUAGES.get(self.language).raid_embed_description_with_location_link.format(
                    raid_id=self.raid_id.strip("'"),
                    raid_type=self.raid_type.strip("'").capitalize(),
                    time_date=f"""{str(self.takes_place_at).strip("'")} {gmt}""",
                    location=location_name.capitalize(),
                    latitude=latitude,
                    longitude=longitude,
                ) if latitude is not None else SUPPORTED_LANGUAGES.get(self.language).raid_embed_description_without_location_link.format(
                    raid_id=self.raid_id.strip("'"),
                    raid_type=self.raid_type.strip("'").capitalize(),
                    time_date=f"""{str(self.takes_place_at).strip("'")} {gmt}""",
                    location=location_name.capitalize(),
                ),
                colour=hikari.Colour(0x8bc683),
            )
            .set_author(name=self.boss.strip("'").replace("-", " ").capitalize(), icon=pokemon_image)
            .set_footer(text=SUPPORTED_LANGUAGES.get(self.language).raid_embed_footer.format(member=raid_creator.display_name, attendees=self.total_attendess))
            .add_field("Instinct:", value=", ".join(instinct for instinct in instinct_members), inline=False)
            .add_field("Mystic:", value=", ".join(mystic for mystic in mystic_members), inline=False)
            .add_field("Valor:", value=", ".join(valor for valor in valor_members), inline=False)
            .add_field("Remote:", value=", ".join(remote for remote in remote_members), inline=False)
        )

        raid_message = self.bot_aware.cache.get_message(self.raid_message_id) or await self.bot_aware.rest.fetch_message(self.raid_message_channel_id, self.raid_message_id)
        await raid_message.edit(embed=embed)
        return True

    async def delete_raid(self) -> None:
        await self.bot_aware.db.delete_raid(self.raid_id, self.guild)
        try:
            raid_message = await self.bot_aware.rest.fetch_message(self.raid_message_channel_id, self.raid_message_id)
            await raid_message.delete()
        except hikari.NotFoundError:
            return
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.raid.delete_raid").error(
                "Unexpected error while trying to delete raid for "
                f"guild_id: {self.guild.id}! Got error: {e}!"
            )