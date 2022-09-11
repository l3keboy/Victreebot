# IMPORTS
import logging
import os

import asyncpg
import hikari
from dotenv import load_dotenv
from utils.helpers.contants import DB_GUILD_LOG_SETTINGS_GENERAL_EVENTS
from utils.helpers.contants import DB_GUILD_LOG_SETTINGS_PROFILE_EVENTS
from utils.helpers.contants import DB_GUILD_LOG_SETTINGS_RAID_EVENTS
from utils.helpers.contants import DB_GUILD_LOG_SETTINGS_TRADE_EVENTS
from utils.helpers.contants import DB_GUILD_SETTINGS_DEFAUTS
from utils.helpers.contants import DB_GUILD_STATS_DETAILS_DEFAULT
from utils.helpers.contants import DB_USER_DETAILS_DEFAULT

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASENAME = os.getenv("DB_DATABASENAME")


# ------------------------------------------------------------------------- #
# DATABASEHANDLER CLASS #
# ------------------------------------------------------------------------- #
class DatabaseHandler:
    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------------- #
    # Connection methods #
    # ------------------------------------------------------------------------- #
    @classmethod
    async def connect(self) -> None:
        """Initialize asyncpg pool"""
        try:
            self._pool = await asyncpg.create_pool(
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASENAME,
                host=DB_HOST,
                port=int(DB_PORT),
            )
            logging.getLogger(f"{BOT_NAME.lower()}.database").info(
                f"Succesfully created connection pool to database: {DB_HOST} - {DB_DATABASENAME}! "
                f"Signed in as user: {DB_USER}"
            )
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.database").error(
                f"Connection pool to database: {DB_HOST} - {DB_DATABASENAME} failed! Got error: {e}"
            )

    async def close(self) -> None:
        """Close asyncpg pool"""
        try:
            await self._pool.close()
            logging.getLogger(f"{BOT_NAME.lower()}.database").info(
                f"Succesfully closed connection pool to database: {DB_HOST} - {DB_DATABASENAME}!"
            )
        except Exception:
            logging.getLogger(f"{BOT_NAME.lower()}.database").error(
                f"Error while closing connection pool to database: {DB_HOST} - {DB_DATABASENAME}!"
            )

    # ------------------------------------------------------------------------- #
    # Insert methods #
    # ------------------------------------------------------------------------- #
    async def insert_guild(self, guild: hikari.Guild) -> None:
        """Insert guild into Guilds database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert guild into "Guilds" database table
                try:
                    await conn.execute(
                        f"""INSERT INTO "Guilds" (guild_id, guild_owner_id)
                        VALUES ({guild.id}, {guild.owner_id})"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild").info(
                        f"Successfully inserted guild_id: {guild.id} into Guilds database table!"
                    )
                except asyncpg.UniqueViolationError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild").warning(
                        f"UniqueViolationError guild_id: {guild.id} already exists in Guilds database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild").error(
                        f"Unexpected error while trying to insert guild_id: {guild.id} "
                        f"into Guilds database table! Got error: {e}!"
                    )

    async def insert_guild_settings(self, guild: hikari.Guild) -> None:
        """Insert guild into Guild_Settings database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert guild into "Guilds_Settings" database table
                try:
                    await conn.execute(
                        f"""INSERT INTO "Guild_Settings" (guild_id,{",".join(s for s in DB_GUILD_SETTINGS_DEFAUTS.keys())})
                        VALUES ({guild.id},{",".join(s_value for s_value in DB_GUILD_SETTINGS_DEFAUTS.values())})"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_settings").info(
                        f"Successfully inserted guild_id: {guild.id} into Guild_Settings database table!"
                    )
                except asyncpg.UniqueViolationError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_settings").warning(
                        f"UniqueViolationError guild_id: {guild.id} already exists in Guild_Settings database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_settings").error(
                        f"Unexpected error while trying to insert guild_id: {guild.id} "
                        f"into Guild_Settings database table! Got error: {e}!"
                    )

    async def insert_guild_log_settings(self, guild: hikari.Guild) -> None:
        """Insert guild into Guild_Log_Settings database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert guild into "Guild_Log_Settings" database table
                try:
                    await conn.execute(
                        f"""INSERT INTO "Guild_Log_Settings"
                        (guild_id,
                        {",".join(s for s in DB_GUILD_LOG_SETTINGS_GENERAL_EVENTS.keys())},
                        {",".join(s for s in DB_GUILD_LOG_SETTINGS_PROFILE_EVENTS.keys())},
                        {",".join(s for s in DB_GUILD_LOG_SETTINGS_RAID_EVENTS.keys())},
                        {",".join(s for s in DB_GUILD_LOG_SETTINGS_TRADE_EVENTS.keys())})
                        VALUES
                        ({guild.id},
                        {",".join(str(s_value) for s_value in DB_GUILD_LOG_SETTINGS_GENERAL_EVENTS.values())},
                        {",".join(str(s_value) for s_value in DB_GUILD_LOG_SETTINGS_PROFILE_EVENTS.values())},
                        {",".join(str(s_value) for s_value in DB_GUILD_LOG_SETTINGS_RAID_EVENTS.values())},
                        {",".join(str(s_value) for s_value in DB_GUILD_LOG_SETTINGS_TRADE_EVENTS.values())})
                        """
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_log_settings").info(
                        f"Successfully inserted guild_id: {guild.id} into Guild_Log_Settings database table!"
                    )
                except asyncpg.UniqueViolationError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_log_settings").warning(
                        f"UniqueViolationError guild_id: {guild.id} already exists in "
                        "Guild_Log_Settings database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_log_settings").error(
                        f"Unexpected error while trying to insert guild_id: {guild.id} "
                        f"into Guild_Log_Settings database table! Got error: {e}!"
                    )

    async def insert_guild_stats(self, guild: hikari.Guild) -> None:
        """Insert guild into Guild_Stats database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert guild into "Guild_Stats" database table
                try:
                    await conn.execute(
                        f"""INSERT INTO "Guild_Stats"
                        (guild_id,
                        {",".join(s for s in DB_GUILD_STATS_DETAILS_DEFAULT.keys())})
                        VALUES
                        ({guild.id},
                        {",".join(str(s_value) for s_value in DB_GUILD_STATS_DETAILS_DEFAULT.values())})
                        """
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_stats").info(
                        f"Successfully inserted guild_id: {guild.id} into Guild_Stats database table!"
                    )
                except asyncpg.UniqueViolationError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_stats").warning(
                        f"UniqueViolationError guild_id: {guild.id} already exists in " "Guild_Stats database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_stats").error(
                        f"Unexpected error while trying to insert guild_id: {guild.id} "
                        f"into Guild_Stats database table! Got error: {e}!"
                    )

    async def insert_user(self, guild: hikari.Guild, user: hikari.User) -> None:
        """Insert user into Users database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert user into "Users" database table
                try:
                    await conn.execute(
                        f"""INSERT INTO "Users" (guild_id,user_id,
                        {",".join(d for d in DB_USER_DETAILS_DEFAULT.keys())})
                        VALUES ({guild.id},{user.id},
                        {",".join(d_value for d_value in DB_USER_DETAILS_DEFAULT.values())})"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_user").info(
                        f"Successfully inserted combination of guild_id: {guild.id} "
                        f"and user_id: {user.id} into Users database table!"
                    )
                except asyncpg.UniqueViolationError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_user").warning(
                        f"UniqueViolationError combination of guild_id: {guild.id} and user_id: "
                        f"{user.id} already exists in Users database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_user").error(
                        f"Unexpected error while trying to insert user_id: {user.id} "
                        f"into Users database table! Got error: {e}!"
                    )

    # ------------------------------------------------------------------------- #
    # Delete methods #
    # ------------------------------------------------------------------------- #
    async def delete_guild(self, guild_id: int) -> None:
        """Delete guild from Guilds database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete guild from "Guilds" database table
                try:
                    await conn.execute(
                        f"""DELETE FROM "Guilds"
                        WHERE guild_id = {guild_id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild").info(
                        f"Successfully deleted guild_id: {guild_id} from Guilds database table!"
                    )
                except Exception:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild").error(
                        f"Unexpected error while trying to delete guild_id: {guild_id} "
                        "from Guilds database table! Got error: {e}!"
                    )

    async def delete_guild_settings(self, guild_id: int) -> None:
        """Delete guild from Guild_Settings database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete guild from "Guilds_Settings" database table
                try:
                    await conn.execute(
                        f"""DELETE FROM "Guild_Settings"
                        WHERE guild_id = {guild_id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_settings").info(
                        f"Successfully deleted guild_id: {guild_id} from Guild_Settings database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_settings").error(
                        f"Unexpected error while trying to delete guild_id: {guild_id} "
                        f"from Guild_Settings database table! Got error: {e}!"
                    )

    async def delete_guild_log_settings(self, guild_id: int) -> None:
        """Delete guild from Guild_Log_Settings database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete guild from "Guild_Log_Settings" database table
                try:
                    await conn.execute(
                        f"""DELETE FROM "Guild_Log_Settings"
                        WHERE guild_id = {guild_id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_log_settings").info(
                        f"Successfully deleted guild_id: {guild_id} from Guild_Log_Settings database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_log_settings").error(
                        f"Unexpected error while trying to delete guild_id: {guild_id} "
                        f"from Guild_Log_Settings database table! Got error: {e}!"
                    )

    async def delete_guild_stats(self, guild_id: int) -> None:
        """Delete guild from Guild_Stats database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete guild from "Guild_Stats" database table
                try:
                    await conn.execute(
                        f"""DELETE FROM "Guild_Stats"
                        WHERE guild_id = {guild_id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_stats").info(
                        f"Successfully deleted guild_id: {guild_id} from Guild_Stats database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_stats").error(
                        f"Unexpected error while trying to delete guild_id: {guild_id} "
                        f"from Guild_Stats database table! Got error: {e}!"
                    )

    async def delete_guild_users(self, guild_id: int) -> None:
        """Delete guild entries from Users database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete guild entries from "Users" database table
                try:
                    await conn.execute(
                        f"""DELETE FROM "Users"
                        WHERE guild_id = {guild_id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_users").info(
                        f"Successfully deleted guild_id: {guild_id} from Users database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_users").error(
                        f"Unexpected error while trying to delete guild_id: {guild_id} "
                        f"from Users database table! Got error: {e}!"
                    )

    async def delete_user(self, guild_id: int, user_id: int) -> None:
        """Delete user from Users database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete user from "Users" database table
                try:
                    await conn.execute(
                        f"""DELETE FROM "Users"
                        WHERE guild_id = {guild_id}
                        AND user_id = {user_id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_user").info(
                        f"Successfully deleted user_id: {user_id} from Users database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_user").error(
                        f"Unexpected error while trying to delete user_id: {user_id} "
                        f"from Users database table! Got error: {e}!"
                    )

    async def delete_guild_locations(self, guild_id: int) -> None:
        """Delete Guild locations from Locations database table"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete Guild locations from "Locations" database table
                try:
                    await conn.execute(
                        f"""DELETE FROM "Locations"
                        WHERE guild_id = {guild_id}
                        AND type = 'gym' OR type = 'pokéstop'"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_locations").info(
                        f"Successfully deleted all locations for guild_id: {guild_id} from Locations database table!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_locations").error(
                        f"Unexpected error while trying to delete locations for guild_id: {guild_id} "
                        f"from Locations database table! Got error: {e}!"
                    )

    # ------------------------------------------------------------------------- #
    # Autocomplete methods #
    # ------------------------------------------------------------------------- #
    async def get_locations_like(self, guild: hikari.Guild, query: str) -> list[str]:
        """Get locations like"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_locations = await conn.fetch(
                        f"""SELECT type, name
                            FROM "Locations"
                            WHERE guild_id = {guild.id} AND name LIKE '%{query}%'"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_locations_like").debug(
                        "Successfully got locations for autocomplete!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_locations_like").error(
                        f"Unexpected error while trying to fetch location for autocomplete! Got error: {e}"
                    )
                    return None
        return fetched_locations

    async def get_raid_id_like(self, guild: hikari.Guild, query: str) -> list[str]:
        """Get locations like"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_raid_ids = await conn.fetch(
                        f"""SELECT raid_id
                            FROM "Raids"
                            WHERE guild_id = {guild.id} AND raid_id LIKE '%{query}%'"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_raid_id_like").debug(
                        "Successfully got raid ID's for autocomplete!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_raid_id_like").error(
                        f"Unexpected error while trying to fetch raid ID's for autocomplete! Got error: {e}"
                    )
                    return None
        return fetched_raid_ids

    # ------------------------------------------------------------------------- #
    # Other methods #
    # ------------------------------------------------------------------------- #
    async def active_servers(self) -> int:
        """Select active serves"""
        active_servers = 0
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    active_servers = await conn.fetch(
                        '''SELECT COUNT("guild_id")
                           FROM "Guilds"'''
                    )
                    active_servers = active_servers[0].get("count")
                    logging.getLogger(f"{BOT_NAME.lower()}.database.active_servers").info(
                        "Successfully got active server count!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.active_servers").error(
                        f"Unexpected error while trying to fetch active server count! Got error: {e}!"
                    )
        return active_servers

    async def get_distinct(self, column: str, table: str):
        """Select disctinct setting"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_distinct = await conn.fetch(
                        f'''SELECT DISTINCT {column}
                            FROM "{table}"'''
                    )
                    results.append(fetched_distinct)
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_distinct").info(
                        f"Successfully got distinct column: {column} in table: {table}!"
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_distinct").error(
                        f"Unexpected error while trying to fetch distinct for column: {column} "
                        f"in table: {table}! Got error: {e}!"
                    )
                    results.append(None)
        return results

    async def set_guild_setting(self, guild: hikari.Guild, parameters: list) -> bool:
        """Set Guild setting"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""UPDATE "Guild_Settings"
                            SET {",".join(change for change in parameters)}
                            WHERE guild_id = {guild.id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_setting").info(
                        f"Successfully updated setting for guild_id: {guild.id}!"
                    )
                    success = True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_setting").error(
                        f"Unexpected error while trying to update setting for guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def get_guild_settings(self, guild: hikari.Guild, settings: list) -> list:
        """Get settings of a guild"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_settings = await conn.fetch(
                        f"""SELECT {",".join(setting for setting in settings)}
                            FROM "Guild_Settings" WHERE guild_id = {guild.id}"""
                    )
                    for setting in fetched_settings[0]:
                        results.append(setting)
                except IndexError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_settings").warning(
                        f"ValueError while trying to fetch settings for guild_id: {guild.id}! "
                        f"Inserting {guild.id} to database with default values and returning default values!"
                    )
                    # Insert guild to database with default settings
                    await self.insert_guild(guild=guild)
                    await self.insert_guild_settings(guild=guild)
                    # Return default values for every requested setting
                    for setting in settings:
                        if setting == "raids_channel_id" or setting == "moderator_role_id":
                            results.append("None")
                        else:
                            results.append(DB_GUILD_SETTINGS_DEFAUTS.get(setting).strip("'"))
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_settings").error(
                        f"Unexpected error while trying to fetch settings for guild_id: {guild.id}! Got error: {e}"
                    )
        return results

    async def set_guild_log_setting(self, guild: hikari.Guild, parameters: list) -> bool:
        """Set Guild log setting"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""UPDATE "Guild_Log_Settings"
                            SET {",".join(change for change in parameters)}
                            WHERE guild_id = {guild.id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_log_setting").info(
                        f"Successfully updated log setting for guild_id: {guild.id}!"
                    )
                    success = True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_log_setting").error(
                        f"Unexpected error while trying to update log setting for guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def get_guild_log_settings(self, guild: hikari.Guild, settings: list) -> list:
        """Get logging settings of a guild"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_settings = await conn.fetch(
                        f"""SELECT {",".join(setting for setting in settings)}
                            FROM "Guild_Log_Settings" WHERE guild_id = {guild.id}"""
                    )
                    for setting in fetched_settings[0]:
                        results.append(setting)
                except IndexError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_log_settings").warning(
                        f"ValueError while trying to fetch log settings for guild_id: {guild.id}! "
                        f"Inserting {guild.id} to database with default values and returning default values!"
                    )
                    # The Guild is not insterted in the database table. Insert and return default values
                    for setting in settings:
                        results.append(None)
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_log_settings").error(
                        f"Unexpected error while trying to fetch log settings for guild_id: {guild.id}! Got error: {e}"
                    )
        return results

    async def set_user_detail(self, guild: hikari.Guild, member: hikari.Member, parameters: list) -> bool:
        """Set user setting"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""UPDATE "Users"
                            SET {",".join(change for change in parameters)}
                            WHERE guild_id = {guild.id}
                            AND user_id = {member.id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_user_detail").info(
                        f"Successfully updated detail for member_id: {member.id} in guild_id: {guild.id}!"
                    )
                    success = True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_user_detail").error(
                        f"Unexpected error while trying to update detail for member_id: {member.id} "
                        f"in guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def get_user_details(self, guild: hikari.Guild, member: hikari.Member, details: list) -> list:
        """Get details of a user"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_details = await conn.fetch(
                        f"""SELECT
                            {",".join(detail for detail in details)}
                            FROM "Users"
                            WHERE guild_id = {guild.id}
                            AND user_id = {member.id}"""
                    )
                    for detail in fetched_details[0]:
                        results.append(detail)
                except IndexError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_user_details").warning(
                        f"ValueError while trying to fetch details for member_id: {member.id} in guild_id: "
                        f"{guild.id}! Inserting member_id: {member.id} to database with default values "
                        "and returning default values!"
                    )
                    # Insert guild to database with default settings
                    await self.insert_user(guild=guild, user=member)
                    # Return default values for every requested setting
                    for detail in details:
                        results.append(DB_USER_DETAILS_DEFAULT.get(detail).strip("'"))
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_user_details").error(
                        f"Unexpected error while trying to fetch details for member_id: {member.id} "
                        f"in guild_id: {guild.id}! Got error: {e}"
                    )
        return results

    async def set_guild_stats(self, guild: hikari.Guild, parameters: list) -> bool:
        """Set guild stats"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""UPDATE "Guild_Stats"
                            SET {",".join(change for change in parameters)}
                            WHERE guild_id = {guild.id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_stats").info(
                        f"Successfully updated stats for guild_id: {guild.id}!"
                    )
                    success = True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_stats").error(
                        "Unexpected error while trying to update stats for " f"guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def get_guild_stats(self, guild: hikari.Guild, stats: list) -> list:
        """Get stats of a guild"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_details = await conn.fetch(
                        f"""SELECT
                            {",".join(stat for stat in stats)}
                            FROM "Guild_Stats"
                            WHERE guild_id = {guild.id}"""
                    )
                    for detail in fetched_details[0]:
                        results.append(detail)
                except IndexError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_stats").warning(
                        f"ValueError while trying to fetch stats for guild_id: "
                        f"{guild.id}! Inserting guild_id with default values "
                        "and returning default values!"
                    )
                    # Insert guild to database with default settings
                    await self.insert_guild_stats(guild=guild)
                    # Return default values for every requested setting
                    for stat in stats:
                        results.append(DB_GUILD_STATS_DETAILS_DEFAULT.get(stat).strip("'"))
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_stats").error(
                        f"Unexpected error while trying to fetch stats for " f"in guild_id: {guild.id}! Got error: {e}"
                    )
        return results

    # ------------------------------------------------------------------------- #
    # Location methods #
    # ------------------------------------------------------------------------- #
    async def insert_location(
        self, guild: hikari.Guild, location_type: str, name: str, latitude: float, longitude: float, description: str
    ) -> bool:
        """Insert a location"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""INSERT INTO "Locations" (guild_id, type, name, latitude, longitude, description)
                            VALUES ({guild.id}, {location_type}, {name}, {latitude}, {longitude}, {description})"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_location").info(
                        f"Successfully inserted location for guild_id: {guild.id}!"
                    )
                    success = True
                except asyncpg.UniqueViolationError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_location").error(
                        "UniqueViolationError while trying to insert location for "
                        f"guild_id: {guild.id}! Combination of guild_id, type and "
                        "name already exists!"
                    )
                    success = False
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_location").error(
                        f"Unexpected error while trying to insert location for guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def edit_location(self, guild: hikari.Guild, location_type: str, name: str, parameters: list) -> bool:
        """Edit a location"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""UPDATE "Locations"
                            SET {",".join(change for change in parameters)}
                            WHERE guild_id = {guild.id} AND type = {location_type} AND name = {name}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.edit_location").info(
                        f"Successfully edited a location for guild_id: {guild.id}!"
                    )
                    success = True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.edit_location").error(
                        f"Unexpected error while trying to edit a location for guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def delete_location(self, guild: hikari.Guild, location_type: str, name: str) -> bool:
        """Delete a location"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""DELETE FROM "Locations"
                            WHERE guild_id = {guild.id} AND type = {location_type} AND name = {name}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_location").info(
                        f"Successfully deleted a location for guild_id: {guild.id}!"
                    )
                    success = True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_location").error(
                        f"Unexpected error while trying to delete a location for guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def get_all_locations(self, guild: hikari.Guild, location_type: str) -> list:
        """Get all locations"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    results = await conn.fetch(
                        f"""SELECT name, latitude, longitude
                            FROM "Locations"
                            WHERE guild_id = {guild.id}
                            AND type = {location_type}"""
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_all_locations").error(
                        f"Unexpected error while trying to fetch all locations for guild_id: {guild.id}! "
                        f"Got error: {e}"
                    )
        return results

    async def get_location_info(self, guild: hikari.Guild, location_type: str, location_name: str) -> list:
        """Get location info"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    results = await conn.fetch(
                        f"""SELECT name, latitude, longitude, description
                            FROM "Locations"
                            WHERE guild_id = {guild.id}
                            AND type = {location_type}
                            AND name = {location_name}"""
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_location_info").error(
                        f"Unexpected error while trying to fetch location for guild_id: {guild.id}! " f"Got error: {e}"
                    )
        return results

    # ------------------------------------------------------------------------- #
    # Raid methods #
    # ------------------------------------------------------------------------- #
    async def insert_raid(
        self,
        guild: hikari.Guild,
        raid_id: str,
        raid_type: str,
        location_type: str,
        location_name: str,
        takes_place_at: str,
        boss: str,
        end_time: str,
        raid_message_channel_id: int,
        raid_message_id: int,
        raid_creator_id: int,
        takes_place_at_to_show: str,
    ) -> bool:
        """Insert a raid"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""INSERT INTO "Raids"
                            (guild_id, raid_id, raid_type, location_type,
                            location_name, takes_place_at, boss, end_time,
                            raid_message_channel_id, raid_message_id, raid_creator_id, takes_place_at_to_show)
                            VALUES
                            ({guild.id}, {raid_id}, {raid_type}, {location_type},
                            {location_name}, {takes_place_at}, {boss}, {end_time},
                            {raid_message_channel_id}, {raid_message_id}, {raid_creator_id}, '{takes_place_at_to_show}')"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_raid").info(
                        f"Successfully inserted raid for guild_id: {guild.id}!"
                    )
                    success = True
                except asyncpg.UniqueViolationError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_raid").error(
                        "UniqueViolationError while trying to insert raid for "
                        f"guild_id: {guild.id}! Combination of guild_id and raid_id "
                        "already exists!"
                    )
                    success = False
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_raid").error(
                        f"Unexpected error while trying to insert raid for guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def delete_raid(self, raid_id: str, guild: hikari.Guild) -> bool:
        """Delete a raid"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""DELETE FROM "Raids"
                            WHERE guild_id = {guild.id} AND raid_id = {raid_id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_raid").info(
                        f"Successfully deleted a raid for guild_id: {guild.id}!"
                    )
                    success = True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_raid").error(
                        f"Unexpected error while trying to delete a raid for guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def get_raid_details(self, raid_id: str, guild: hikari.Guild, details: list) -> list:
        """Get raid info"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_details = await conn.fetch(
                        f"""SELECT *
                            FROM "Raids"
                            WHERE guild_id = {guild.id}
                            AND raid_id = {raid_id}"""
                    )
                    for detail in fetched_details[0]:
                        results.append(detail)
                except IndexError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_raid_details").warning(
                        f"ValueError while trying to fetch details for raid_id: {raid_id} in guild_id: "
                        f"{guild.id}! Returning default values!"
                    )
                    # Return default values for every requested setting
                    for detail in details:
                        results.append(None)
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_raid_details").error(
                        f"Unexpected error while trying to fetch raid for guild_id: {guild.id}! " f"Got error: {e}"
                    )
        return results

    async def get_raid_details_by_message(self, message: hikari.Message, guild: hikari.Guild, details: list) -> list:
        """Get raid info"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_details = await conn.fetch(
                        f"""SELECT {",".join(detail for detail in details)}
                            FROM "Raids"
                            WHERE guild_id = {guild.id}
                            AND raid_message_id = {message.id}"""
                    )
                    for detail in fetched_details[0]:
                        results.append(detail)
                except IndexError:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_raid_details_by_message").warning(
                        f"ValueError while trying to fetch details for message_id: {message.id} in guild_id: "
                        f"{guild.id}! Returning default values!"
                    )
                    # Return default values for every requested setting
                    for detail in details:
                        results.append(None)
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_raid_details_by_message").error(
                        f"Unexpected error while trying to fetch raid for guild_id: {guild.id}! " f"Got error: {e}"
                    )
        return results

    async def set_raid_detail(self, guild: hikari.Guild, raid_id: str, parameters: list) -> bool:
        """Set raid detail"""
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        f"""UPDATE "Raids"
                            SET {",".join(change for change in parameters)}
                            WHERE guild_id = {guild.id} AND raid_id = {raid_id}"""
                    )
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_raid_detail").info(
                        f"Successfully updated raid for guild_id: {guild.id}!"
                    )
                    success = True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_raid_detail").error(
                        "Unexpected error while trying to update raid for " f"guild_id: {guild.id}! Got error: {e}!"
                    )
                    success = False
        return success

    async def get_all_raids(self) -> list:
        """Get all raids"""
        results = []
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    results = await conn.fetch(
                        """SELECT *
                           FROM "Raids" """
                    )
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_all_raids").error(
                        f"Unexpected error while trying to fetch all raids! " f"Got error: {e}"
                    )
        return results
