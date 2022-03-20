# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
# Logging
import logging
# Own Files
from utils.helpers.constants import DB_GUILD_SETTINGS_DEFAUTS, DB_GUILD_LOG_SETTINGS_DEFAUTS, DB_USER_DEFAUTS
# Hikari
import hikari
# Database and .env
import os
from dotenv import load_dotenv
import asyncpg


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
        """ Initialize asyncpg pool """
        try:
            self._pool = await asyncpg.create_pool(            
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASENAME,
                host=DB_HOST,
                port=int(DB_PORT),
            )
            logging.getLogger(f"{BOT_NAME.lower()}.database").info(f"Succesfully created connection pool to database: {DB_HOST} - {DB_DATABASENAME}! Signed in as user: {DB_USER}")
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.database").error(f"Connection pool to database: {DB_HOST} - {DB_DATABASENAME} failed! Got error: {e}")

    async def close(self) -> None:
        """ Close asyncpg pool """
        try:
            await self._pool.close()
            logging.getLogger(f"{BOT_NAME.lower()}.database").info(f"Succesfully closed connection pool to database: {DB_HOST} - {DB_DATABASENAME}!")
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.database").error(f"Error while closing connection pool to database: {DB_HOST} - {DB_DATABASENAME}!")

    # ------------------------------------------------------------------------- #
    # Insert methods #
    # ------------------------------------------------------------------------- #
    async def insert_guild(self, guild: hikari.Guild) -> None:
        """ Insert guild into Guilds database table """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert guild into "Guilds" database table
                try:
                    await conn.execute(f'INSERT INTO "Guilds" (guild_id, guild_owner_id) VALUES ({guild.id}, {guild.owner_id})')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild").info(f"Successfully inserted guild_id: {guild.id} into Guilds database table!")
                except asyncpg.UniqueViolationError as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild").warning(f"UniqueViolationError guild_id: {guild.id} already exists in Guilds database table!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild").error(f"Unexpected error while trying to insert guild_id: {guild.id} into Guilds database table! Got error: {e}!")
    
    async def insert_guild_settings(self, guild: hikari.Guild) -> None:
        """ Insert guild into Guild_Settings database table """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert guild into "Guilds_Settings" database table
                try:
                    await conn.execute(f'INSERT INTO "Guild_Settings" (guild_id,{",".join(setting for setting in DB_GUILD_SETTINGS_DEFAUTS.keys())}) VALUES ({guild.id},{",".join(settings_value for settings_value in DB_GUILD_SETTINGS_DEFAUTS.values())})')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_settings").info(f"Successfully inserted guild_id: {guild.id} into Guild_Settings database table!")
                except asyncpg.UniqueViolationError as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_settings").warning(f"UniqueViolationError guild_id: {guild.id} already exists in Guild_Settings database table!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_settings").error(f"Unexpected error while trying to insert guild_id: {guild.id} into Guild_Settings database table! Got error: {e}!")

    async def insert_guild_log_settings(self, guild: hikari.Guild) -> None:
        """ Insert guild into Guild_Log_Settings database table """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert guild into "Guilds_Log_Settings" database table
                try:
                    await conn.execute(f'INSERT INTO "Guild_Log_Settings" (guild_id,{",".join(setting for setting in DB_GUILD_LOG_SETTINGS_DEFAUTS.keys())}) VALUES ({guild.id},{",".join(settings_value for settings_value in DB_GUILD_LOG_SETTINGS_DEFAUTS.values())})')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_log_settings").info(f"Successfully inserted guild_id: {guild.id} into Guild_Log_Settings database table!")
                except asyncpg.UniqueViolationError as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_log_settings").warning(f"UniqueViolationError guild_id: {guild.id} already exists in Guild_Log_Settings database table!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_guild_log_settings").error(f"Unexpected error while trying to insert guild_id: {guild.id} into Guild_Log_Settings database table! Got error: {e}!")

    async def insert_user(self, guild: hikari.Guild, member: hikari.Member) -> None:
        """ Insert user into Users database table """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert user into "Users" database table
                try:
                    await conn.execute(f'INSERT INTO "Users" (guild_id,user_id,{",".join(detail for detail in DB_USER_DEFAUTS.keys())}) VALUES ({guild.id},{member.id},{",".join(detail_value for detail_value in DB_USER_DEFAUTS.values())})')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_user").info(f"Successfully inserted combination of guild_id: {guild.id} and user_id: {member.id} into Users database table!")
                except asyncpg.UniqueViolationError as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_user").warning(f"UniqueViolationError combination of guild_id: {guild.id} and user_id: {member.id} already exists in Users database table!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.insert_user").error(f"Unexpected error while trying to insert user_id: {member.id} into Users database table! Got error: {e}!")

    # ------------------------------------------------------------------------- #
    # Delete methods #
    # ------------------------------------------------------------------------- #
    async def delete_guild(self, guild: hikari.Guild) -> None:
        """ Delete guild from Guilds database table """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete guild from "Guilds" database table
                try:
                    await conn.execute(f'DELETE FROM "Guilds" WHERE guild_id = {guild.id}')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild").info(f"Successfully deleted guild_id: {guild.id} from Guilds database table!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild").error(f"Unexpected error while trying to delete guild_id: {guild.id} from Guilds database table! Got error: {e}!")

    async def delete_guild_settings(self, guild: hikari.Guild) -> None:
        """ Delete guild from Guild_Settings database table """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete guild from "Guilds_Settings" database table
                try:
                    await conn.execute(f'DELETE FROM "Guild_Settings" WHERE guild_id = {guild.id}')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_settings").info(f"Successfully deleted guild_id: {guild.id} from Guild_Settings database table!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_settings").error(f"Unexpected error while trying to delete guild_id: {guild.id} from Guild_Settings database table! Got error: {e}!")

    async def delete_guild_log_settings(self, guild: hikari.Guild) -> None:
        """ Delete guild from Guild_Log_Settings database table """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete guild from "Guilds_Log_Settings" database table
                try:
                    await conn.execute(f'DELETE FROM "Guild_Log_Settings" WHERE guild_id = {guild.id}')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_log_settings").info(f"Successfully deleted guild_id: {guild.id} from Guild_Log_Settings database table!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_log_settings").error(f"Unexpected error while trying to delete guild_id: {guild.id} from Guild_Log_Settings database table! Got error: {e}!")

    async def delete_guild_users(self, guild: hikari.Guild) -> None:
        """ Delete guild entries from Users database table """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete guild entries from "Users" database table
                try:
                    await conn.execute(f'DELETE FROM "Users" WHERE guild_id = {guild.id}')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_users").info(f"Successfully deleted guild_id: {guild.id} from Users database table!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_guild_users").error(f"Unexpected error while trying to delete guild_id: {guild.id} from Users database table! Got error: {e}!")

    async def delete_user(self, guild: hikari.Guild, member: hikari.Member) -> None:
        """ Delete user from Users database table """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Delete user from "Users" database table
                try:
                    await conn.execute(f'DELETE FROM "Users" WHERE guild_id = {guild.id} AND user_id = {member.id}')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_user").info(f"Successfully deleted user_id: {member.id} from Users database table!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.delete_user").error(f"Unexpected error while trying to delete user_id: {member.id} from Users database table! Got error: {e}!")

    # ------------------------------------------------------------------------- #
    # Other methods #
    # ------------------------------------------------------------------------- #
    async def active_servers(self) -> int:
        """ Select active serves """
        active_servers=0
        async with self._pool.acquire() as conn:
            async with conn.transaction():                    
                try:
                    active_servers = await conn.fetch(f'SELECT COUNT("guild_id") FROM "Guilds"')
                    active_servers = active_servers[0].get("count")
                    logging.getLogger(f"{BOT_NAME.lower()}.database.active_servers").info(f"Successfully got active server count!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.active_servers").error(f"Unexpected error while trying to fetch active server count! Got error: {e}!")
        return active_servers

    async def get_distinct(self, column: str, table: str):
        """ Select disctinct setting """
        results=[]
        async with self._pool.acquire() as conn:
            async with conn.transaction():                    
                try:
                    fetched_distinct = await conn.fetch(f'SELECT DISTINCT {column} FROM "{table}"')
                    results.append(fetched_distinct)
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_distinct").info(f"Successfully got distinct column: {column} in table: {table}!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_distinct").error(f"Unexpected error while trying to fetch distinct for column: {column} in table: {table}! Got error: {e}!")
                    results.append(None)
        return results

    async def set_guild_setting(self, guild: hikari.Guild, parameters: list) -> bool:
        """ Set Guild setting """
        async with self._pool.acquire() as conn:
            async with conn.transaction():                    
                try:
                    await conn.execute(f'UPDATE "Guild_Settings" SET {",".join(change for change in parameters)} WHERE guild_id = {guild.id}')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_setting").info(f"Successfully updated setting for guild_id: {guild.id}!")
                    success=True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_setting").error(f"Unexpected error while trying to update setting for guild_id: {guild.id}! Got error: {e}!")
                    success=False
        return success

    async def get_guild_settings(self, guild: hikari.Guild, settings: list) -> list:
        """ Get settings of a guild """
        results=[]
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_settings = await conn.fetch(f'SELECT {",".join(setting for setting in settings)} FROM "Guild_Settings" WHERE guild_id = {guild.id}')
                    for setting in fetched_settings[0]:
                        results.append(setting)
                except IndexError as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_settings").warning(f"ValueError while trying to fetch settings for guild_id: {guild.id}! Inserting {guild.id} to database with default values and returning default values!")
                    # Insert guild to database with default settings
                    await self.insert_guild(guild=guild)
                    await self.insert_guild_settings(guild=guild)
                    # Return default values for every requested setting
                    for setting in settings:
                        results.append(DB_GUILD_SETTINGS_DEFAUTS.get(setting).strip("'"))
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_settings").error(f"Unexpected error while trying to fetch settings for guild_id: {guild.id}! Got error: {e}")
        return results

    async def set_guild_log_setting(self, guild: hikari.Guild, parameters: list) -> bool:
        """ Set Guild log setting """
        async with self._pool.acquire() as conn:
            async with conn.transaction():                    
                try:
                    await conn.execute(f'UPDATE "Guild_Log_Settings" SET {",".join(change for change in parameters)} WHERE guild_id = {guild.id}')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_log_setting").info(f"Successfully updated log setting for guild_id: {guild.id}!")
                    success=True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_guild_log_setting").error(f"Unexpected error while trying to update log setting for guild_id: {guild.id}! Got error: {e}!")
                    success=False
        return success

    async def get_guild_log_settings(self, guild: hikari.Guild, settings: list) -> list:
        """ Get settings of a guild """
        results=[]
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_settings = await conn.fetch(f'SELECT {",".join(setting for setting in settings)} FROM "Guild_Log_Settings" WHERE guild_id = {guild.id}')
                    for setting in fetched_settings[0]:
                        results.append(setting)
                except IndexError as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_log_settings").warning(f"ValueError while trying to fetch log settings for guild_id: {guild.id}! Inserting {guild.id} to database with default values and returning default values!")
                    # Insert guild to database with default settings
                    await self.insert_guild(guild=guild)
                    await self.insert_guild_settings(guild=guild)
                    await self.insert_guild_log_settings(guild=guild)
                    # Return default values for every requested setting
                    for setting in settings:
                        if setting == "logs_channel_id":
                            results.append("None")
                        else:
                            results.append(DB_GUILD_LOG_SETTINGS_DEFAUTS.get(setting).strip("'"))
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_guild_log_settings").error(f"Unexpected error while trying to fetch log settings for guild_id: {guild.id}! Got error: {e}")
        return results

    async def set_user_detail(self, guild: hikari.Guild, member: hikari.Member, detail: str, value: str|int) -> bool:
        """ Set user setting """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Set guild setting
                if isinstance(value, str):
                    value = "'" + value + "'"
                if value == "'NULL'":
                    value = "NULL"
                    
                try:
                    await conn.execute(f'UPDATE "Users" SET {detail} = {value} WHERE guild_id = {guild.id} AND user_id = {member.id}')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_user_detail").info(f"Successfully updated detail for member_id: {member.id} in guild_id: {guild.id}!")
                    success=True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_user_detail").error(f"Unexpected error while trying to update detail for member_id: {member.id} in guild_id: {guild.id}! Got error: {e}!")
                    success=False
        return success

    async def get_user_details(self, guild: hikari.Guild, member: hikari.Member, details: list) -> list:
        """ Get details of a user """
        results=[]
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    fetched_details = await conn.fetch(f'SELECT {",".join(detail for detail in details)} FROM "Users" WHERE guild_id = {guild.id} AND user_id = {member.id}')
                    for detail in fetched_details[0]:
                        results.append(detail)
                except IndexError as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_user_details").warning(f"ValueError while trying to fetch details for member_id: {member.id} in guild_id: {guild.id}! Inserting member_id: {member.id} to database with default values and returning default values!")
                    # Insert guild to database with default settings
                    await self.insert_user(guild=guild, member=member)
                    # Return default values for every requested setting
                    for detail in details:
                        results.append(DB_USER_DEFAUTS.get(detail).strip("'"))
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.get_user_details").error(f"Unexpected error while trying to fetch details for member_id: {member.id} in guild_id: {guild.id}! Got error: {e}")
        return results

    async def check_deny(self, member: hikari.Member, deny_to_check: str) -> bool:
        """ Check if a user is denied """
        deny=False
        async with self._pool.acquire() as conn:
            async with conn.transaction():                    
                try:
                    fetched_deny = await conn.fetch(f'SELECT {deny_to_check} FROM "Users" WHERE user_id = {member.id}')
                    deny = fetched_deny[0].get(deny_to_check)
                    logging.getLogger(f"{BOT_NAME.lower()}.database.check_deny").info(f"Successfully checked deny for member: {member.id}!")
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.check_deny").error(f"Unexpected error while trying to check deny for member: {member.id}! Got error: {e}!")
        return deny

    async def set_deny(self, member: hikari.Member, deny_to_set: str, value: bool, admin: hikari.Member) -> bool:
        """ Set a deny for a user to true or false """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(f'UPDATE "Users" SET {deny_to_set} = {value} WHERE user_id = {member.id}')
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_deny").info(f"Successfully updated {deny_to_set} for user: {member.id} - admin: {admin.username}!")
                    success=True
                except Exception as e:
                    logging.getLogger(f"{BOT_NAME.lower()}.database.set_deny").error(f"Unexpected error while trying to update {deny_to_set} for user: {member.id} - admin: {admin.username}! Got error: {e}!")
                    success=False
        return success
