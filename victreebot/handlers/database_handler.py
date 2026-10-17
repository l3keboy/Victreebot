# IMPORTS
from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor  # pyright: ignore[reportMissingTypeStubs]
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import and_, select

from victreebot.exceptions.DatabaseError import DatabaseError
from victreebot.models.GuildStats import Guild_Stats, Guild_StatsUpdate
from victreebot.models.Guilds import Guilds
from victreebot.models.GuildLogSettings import Guild_Log_Settings, Guild_Log_SettingsUpdate
from victreebot.models.GuildSettings import Guild_Settings, Guild_SettingsUpdate
from victreebot.models.Users import Users, UsersUpdate
from victreebot.models.Locations import Locations, LocationsUpdate
from victreebot.models.Raids import Raids, RaidsUpdate
from victreebot.utils.EnvVarLoader import EnvVarLoader

if TYPE_CHECKING:
    from collections.abc import Sequence

    import hikari

    from victreebot.core.bot import Bot


# ------------------------------------------------------------------------- #
# DatabaseHandler class #
# ------------------------------------------------------------------------- #
class DatabaseHandler:
    """Handler to interact with the Victreebot database."""

    _app: Bot
    engine: AsyncEngine
    connection_string: str

    def __init__(self, app: Bot) -> None:
        self._app = app
        self.connection_string = (
            f"postgresql+asyncpg://{EnvVarLoader.load_env_variable('DB_USER')}"
            f":{quote_plus(EnvVarLoader.load_env_variable('DB_PASSWORD'))}"
            f"@{self._app.vars.DB_HOST}:{self._app.vars.DB_PORT}/{self._app.vars.DB_DATABASENAME}"
        )

    # ------------------------------------------------------------------------- #
    # Lifetime #
    # ------------------------------------------------------------------------- #
    async def create_engine(self) -> None:
        """Create an SQLalchemy engine."""
        self.engine = create_async_engine(self.connection_string)
        SQLAlchemyInstrumentor().instrument(engine=self.engine.sync_engine)

    async def ping(self) -> bool:
        """Ping the database to check if it's alive."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.execute(select(1))
        except Exception:
            logging.getLogger(__name__).exception("Database ping failed.")
            return False
        return True

    # ------------------------------------------------------------------------- #
    # Guild settings methods #
    # ------------------------------------------------------------------------- #
    async def insert_guild(
        self, guild_id: hikari.Snowflake | int, guild_owner_id: hikari.Snowflake | int
    ) -> Guilds | None:
        """Insert a guild."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.execute(
                    insert(Guilds).values(
                        guild_id=guild_id,
                        guild_owner_id=guild_owner_id,
                    )
                )
                await session.commit()

                fetched_guilds = await session.scalars(
                    select(Guilds).where(
                        (Guilds.guild_id == guild_id)
                        & (Guilds.guild_owner_id == guild_owner_id)
                    )
                )
                final_guild = fetched_guilds.first()
                return final_guild
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_guild(self, guild: Guilds) -> Guilds:
        """Delete a guild."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.delete(guild)
                await session.commit()

                return guild
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_guilds(self) -> Sequence[Guilds]:
        """Get a guild."""
        try:
            async with AsyncSession(self.engine) as session:
                fetched_guilds = await session.scalars(select(Guilds))
                final_guilds = fetched_guilds.all()

                return final_guilds
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_guild(self, guild_id: hikari.Snowflake | int) -> Guilds | None:
        """Get a guild."""
        try:
            async with AsyncSession(self.engine) as session:
                fetched_guilds = await session.scalars(select(Guilds).where(Guilds.guild_id == guild_id))
                final_guild = fetched_guilds.first()

                return final_guild
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def insert_guild_settings(
        self, guild_id: hikari.Snowflake
    ) -> Guild_Settings | None:
        """Insert guild settings."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.execute(
                    insert(Guild_Settings).values(
                        guild_id=guild_id,
                        language="en",
                        gmt="Europe/Amsterdam",
                        unit_system="Metric System",
                        auto_delete=5,
                        raids_channel_id=None,
                        is_setup=False,
                        moderator_role_id=None,
                        instinct_role_id=None,
                        mystic_role_id=None,
                        valor_role_id=None,
                        instinct_emoji_id=None,
                        mystic_emoji_id=None,
                        valor_emoji_id=None,
                        raid_timeout=900,
                        extended_time_format=False,
                    )
                )
                await session.commit()

                fetched_guilds = await session.scalars(
                    select(Guild_Settings).where(
                        (Guild_Settings.guild_id == guild_id)
                    )
                )
                final_guild = fetched_guilds.first()
                return final_guild
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_guild_settings(self, guild_settings: Guild_Settings) -> Guild_Settings:
        """Delete a guilds settings."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.delete(guild_settings)
                await session.commit()

                return guild_settings
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_guild_settings(self, guild_id: hikari.Snowflake | int) -> Guild_Settings | None:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_settings = await session.scalars(
                    select(Guild_Settings).where(
                        Guild_Settings.guild_id == guild_id
                    )
                )
                final_settings = fetched_settings.first()
                return final_settings
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def change_guild_settings(
        self, settings: Guild_Settings, new_settings: Guild_SettingsUpdate
    ) -> Guild_Settings:
        try:
            async with AsyncSession(self.engine) as session:
                settings.sqlmodel_update(new_settings.model_dump(exclude_unset=True))
                settings.guild_id = settings.guild_id

                session.add(settings)
                await session.commit()
                await session.refresh(settings)

                return settings
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    # ------------------------------------------------------------------------- #
    # Guild log settings methods #
    # ------------------------------------------------------------------------- #
    async def insert_guild_log_settings(
        self, guild_id: hikari.Snowflake
    ) -> Guild_Log_Settings | None:
        """Insert guild log settings."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.execute(
                    insert(Guild_Log_Settings).values(
                        guild_id=guild_id,
                        logs_channel_id=None,
                        log_errors=True,
                        log_info=True,
                        log_settings_changed=True,
                        log_profile_edit=True,
                        log_profile_view=True,
                        log_location_add=True,
                        log_location_delete=True,
                        log_location_edit=True,
                        log_location_info=True,
                        log_location_list=True,
                        log_raid_create=True,
                        log_raid_edit=True,
                        log_raid_delete=True,
                        log_trade_offer=True,
                        log_trade_proposal=True,
                        log_trade_search=True,
                    )
                )
                await session.commit()

                fetched_guilds = await session.scalars(
                    select(Guild_Log_Settings).where(
                        (Guild_Log_Settings.guild_id == guild_id)
                    )
                )
                final_guild = fetched_guilds.first()
                return final_guild
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_guild_log_settings(self, guild_log_settings: Guild_Log_Settings) -> Guild_Log_Settings:
        """Delete a guilds log settings."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.delete(guild_log_settings)
                await session.commit()

                return guild_log_settings
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_guild_log_settings(self, guild_id: hikari.Snowflake | int) -> Guild_Log_Settings | None:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_settings = await session.scalars(
                    select(Guild_Log_Settings).where(
                        Guild_Log_Settings.guild_id == guild_id
                    )
                )
                final_settings = fetched_settings.first()
                return final_settings
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def change_guild_log_settings(
        self, settings: Guild_Log_Settings, new_settings: Guild_Log_SettingsUpdate
    ) -> Guild_Log_Settings:
        try:
            async with AsyncSession(self.engine) as session:
                settings.sqlmodel_update(new_settings.model_dump(exclude_unset=True))
                settings.guild_id = settings.guild_id

                session.add(settings)
                await session.commit()
                await session.refresh(settings)

                return settings
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    # ------------------------------------------------------------------------- #
    # Guild stats methods #
    # ------------------------------------------------------------------------- #
    async def insert_guild_stats(
        self, guild_id: hikari.Snowflake
    ) -> Guild_Stats | None:
        """Insert guild stats."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.execute(
                    insert(Guild_Stats).values(
                        guild_id=guild_id,
                        raids_completed=0,
                        raids_deleted=0,
                        raids_created=0
                    )
                )
                await session.commit()

                fetched_guilds = await session.scalars(
                    select(Guild_Stats).where(
                        (Guild_Stats.guild_id == guild_id)
                    )
                )
                final_guild = fetched_guilds.first()
                return final_guild
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_guild_stats(self, guild_stats: Guild_Stats) -> Guild_Stats:
        """Delete a guilds stats."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.delete(guild_stats)
                await session.commit()

                return guild_stats
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_guild_stats(self, guild_id: hikari.Snowflake | int) -> Guild_Stats | None:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_settings = await session.scalars(
                    select(Guild_Stats).where(
                        Guild_Stats.guild_id == guild_id
                    )
                )
                final_settings = fetched_settings.first()
                return final_settings
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def change_guild_stats_settings(
        self, stats: Guild_Stats, new_stats: Guild_StatsUpdate
    ) -> Guild_Stats:
        try:
            async with AsyncSession(self.engine) as session:
                stats.sqlmodel_update(new_stats.model_dump(exclude_unset=True))
                stats.guild_id = stats.guild_id

                session.add(stats)
                await session.commit()
                await session.refresh(stats)

                return stats
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    # ------------------------------------------------------------------------- #
    # User methods #
    # ------------------------------------------------------------------------- #
    async def insert_user(
        self, guild_id: hikari.Snowflake, user_id: hikari.Snowflake
    ) -> Users | None:
        """Insert user."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.execute(
                    insert(Users).values(
                        guild_id=guild_id,
                        user_id=user_id,
                        friend_codes=None,
                        active_locations=None,
                        stats_raids_created=0,
                        stats_raids_participated=0,
                    )
                )
                await session.commit()

                fetched_users = await session.scalars(
                    select(Users).where(
                        (Users.guild_id == guild_id) & (Users.user_id == user_id)
                    )
                )
                final_user = fetched_users.first()
                return final_user
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_users(self, users: Sequence[Users]) -> Sequence[Users]:
        """Delete a user."""
        try:
            async with AsyncSession(self.engine) as session:
                for user in users:
                    await session.delete(user)
                await session.commit()

                return users
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_user(self, user: Users) -> Users:
        """Delete a user."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.delete(user)
                await session.commit()

                return user
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_user_for_guild(self, guild_id: hikari.Snowflake | int, user_id: hikari.Snowflake | int) -> Users | None:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_users = await session.scalars(
                    select(Users).where(
                        (Users.guild_id == guild_id) 
                        & (Users.user_id == user_id)
                    )
                )
                final_user = fetched_users.first()
                return final_user
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_users_for_guild(self, guild_id: hikari.Snowflake | int) -> Sequence[Users]:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_users = await session.scalars(
                    select(Users).where(
                        (Users.guild_id == guild_id) 
                    )
                )
                final_users = fetched_users.all()
                return final_users
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def change_user(
        self, user: Users, new_user: UsersUpdate
    ) -> Users:
        try:
            async with AsyncSession(self.engine) as session:
                user.sqlmodel_update(new_user.model_dump(exclude_unset=True))
                user.guild_id = user.guild_id

                session.add(user)
                await session.commit()
                await session.refresh(user)

                return user
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    # ------------------------------------------------------------------------- #
    # Location methods #
    # ------------------------------------------------------------------------- #
    async def insert_location(
        self, guild_id: hikari.Snowflake, location_type: str, name: str, latitude: float| None , longitude: float| None , description: str | None
    ) -> Locations | None:
        """Insert location."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.execute(
                    insert(Locations).values(
                        guild_id=guild_id,
                        type=location_type,
                        name=name,
                        latitude=latitude,
                        longitude=longitude,
                        description=description
                    )
                )
                await session.commit()

                fetched_locations = await session.scalars(
                    select(Locations).where(
                        (Locations.guild_id == guild_id) 
                        & (Locations.type == location_type) 
                        & (Locations.name == name)
                    )
                )
                final_location = fetched_locations.first()
                return final_location
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_locations(self, locations: Sequence[Locations]) -> Sequence[Locations]:
        """Delete locations."""
        try:
            async with AsyncSession(self.engine) as session:
                for location in locations:
                    await session.delete(location)
                await session.commit()

                return locations
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_location(self, location: Locations) -> Locations:
        """Delete a location."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.delete(location)
                await session.commit()

                return location
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_locations_for_guild(self, guild_id: hikari.Snowflake | int) -> Sequence[Locations]:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_location = await session.scalars(
                    select(Locations).where(
                        (Locations.guild_id == guild_id) 
                    )
                )
                final_locations = fetched_location.all()
                return final_locations
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_locations_by_type(self, guild_id: hikari.Snowflake | int, location_type: str) -> Sequence[Locations]:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_location = await session.scalars(
                    select(Locations).where(
                        (Locations.guild_id == guild_id) 
                        & (Locations.type == location_type) 
                    )
                )
                final_locations = fetched_location.all()
                return final_locations
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_location(self, guild_id: hikari.Snowflake | int, location_type: str, location_name: str) -> Locations | None:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_location = await session.scalars(
                    select(Locations).where(
                        (Locations.guild_id == guild_id) 
                        & (Locations.type == location_type) 
                        & (Locations.name == location_name) 
                    )
                )
                final_location = fetched_location.first()
                return final_location
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def change_location(
        self, location: Locations, new_location: LocationsUpdate
    ) -> Locations:
        try:
            async with AsyncSession(self.engine) as session:
                location.sqlmodel_update(new_location.model_dump(exclude_unset=True))
                location.guild_id = location.guild_id

                session.add(location)
                await session.commit()
                await session.refresh(location)

                return location
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def autocomplete_get_locations_like(
        self, guild_id: hikari.Snowflake, location_format: str
    ) -> Sequence[Locations]:
        """Get locations based on an input."""
        try:
            async with AsyncSession(self.engine) as session:
                fetched_locations = await session.scalars(
                    select(Locations).where(
                        and_(
                            Locations.guild_id== guild_id,
                            Locations.name.like(f"%{location_format}%"),  # type: ignore[attr-defined]
                        )
                    )
                )
                final_locations = fetched_locations.all()
                return final_locations
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    # ------------------------------------------------------------------------- #
    # Raid methods #
    # ------------------------------------------------------------------------- #
    async def insert_raid(
        self, 
        guild_id: hikari.Snowflake | int,
        raid_id: str,
        raid_type: str,
        location_type: str,
        location_name: str,
        takes_place_at: str,
        boss: str,
        end_time: float,
        raid_message_channel_id: int,
        raid_message_id: int,
        raid_creator_id: int,
        takes_place_at_to_show: str,
    ) -> Raids | None:
        """Insert raid."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.execute(
                    insert(Raids).values(
                        guild_id=guild_id,
                        raid_id=raid_id,
                        raid_type=raid_type,
                        location_type=location_type,
                        location_name=location_name,
                        takes_place_at=takes_place_at,
                        boss=boss,
                        end_time=end_time,
                        raid_message_channel_id=raid_message_channel_id,
                        raid_message_id=raid_message_id,
                        raid_creator_id=raid_creator_id,
                        takes_place_at_to_show=takes_place_at_to_show,
                    )
                )
                await session.commit()

                fetched_raids = await session.scalars(
                    select(Raids).where(
                        (Raids.guild_id == guild_id) 
                        & (Raids.raid_id == raid_id) 
                    )
                )
                final_raid = fetched_raids.first()
                return final_raid
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_raids(self, raids: Sequence[Raids]) -> Sequence[Raids]:
        """Delete a raid."""
        try:
            async with AsyncSession(self.engine) as session:
                for raid in raids:
                    await session.delete(raid)
                await session.commit()

                return raids
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def delete_raid(self, raid: Raids) -> Raids:
        """Delete a raid."""
        try:
            async with AsyncSession(self.engine) as session:
                await session.delete(raid)
                await session.commit()

                return raid
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_distinct_raid_id(self) -> Sequence[str]:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_raid_ids = await session.scalars(select(Raids.raid_id).distinct())
                raid_ids = fetched_raid_ids.all()

                return raid_ids
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e
    
    async def get_all_raids(self) -> Sequence[Raids]:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_raid = await session.scalars(
                    select(Raids)
                )
                final_raids = fetched_raid.all()
                return final_raids
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_raids_for_guild(self, guild_id: hikari.Snowflake | int) -> Sequence[Raids]:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_raid = await session.scalars(
                    select(Raids).where(
                        (Raids.guild_id == guild_id) 
                    )
                )
                final_raids = fetched_raid.all()
                return final_raids
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e
        
    async def get_raid(self, guild_id: hikari.Snowflake | int, raid_id: str) -> Raids | None:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_raid = await session.scalars(
                    select(Raids).where(
                        (Raids.guild_id == guild_id) 
                        & (Raids.raid_id == raid_id)
                    )
                )
                final_raid = fetched_raid.first()
                return final_raid
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def get_raid_by_message_id(self, guild_id: hikari.Snowflake | int, raid_message_id: hikari.Snowflake | int) -> Raids | None:
        try:
            async with AsyncSession(self.engine) as session:
                fetched_raid = await session.scalars(
                    select(Raids).where(
                        (Raids.guild_id == guild_id) 
                        & (Raids.raid_message_id == raid_message_id)
                    )
                )
                final_raid = fetched_raid.first()
                return final_raid
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def change_raid(
        self, raid: Raids, new_raid: RaidsUpdate
    ) -> Raids:
        try:
            async with AsyncSession(self.engine) as session:
                raid.sqlmodel_update(new_raid.model_dump(exclude_unset=True))
                raid.guild_id = raid.guild_id

                session.add(raid)
                await session.commit()
                await session.refresh(raid)

                return raid
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

    async def autocomplete_get_raid_id_like(
        self, guild_id: hikari.Snowflake, raid_id_format: str
    ) -> Sequence[Raids]:
        """Get raid IDs based on an input."""
        try:
            async with AsyncSession(self.engine) as session:
                fetched_raid_ids = await session.scalars(
                    select(Raids).where(
                        and_(
                            Raids.guild_id== guild_id,
                            Raids.raid_id.like(f"%{raid_id_format}%"),  # type: ignore[attr-defined]
                        )
                    )
                )
                final_raid_ids = fetched_raid_ids.all()
                return final_raid_ids
        except Exception as e:
            logging.getLogger(__name__).exception("Got unexpected error while interacting with the database")
            raise DatabaseError from e

