# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #
# IMPORTS
# Own files
from utils import DatabaseHandler
from language import en
from utils.LoggingHandler import LoggingHandler

# ------------------------------------------------------------------------- #
# ALL SETTINGS #
# ------------------------------------------------------------------------- #
# Get all settings of a server
async def get_all_settings(guild_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_all_settings = f'SELECT * FROM "Settings" WHERE guild_id = {guild_id}'
            fetched_all_settings = await conn.fetch(select_all_settings)
            
            try:
                language = fetched_all_settings[0].get("language")
                gmt = fetched_all_settings[0].get("gmt")
                auto_delete_time = int(fetched_all_settings[0].get("auto_delete_time"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_all_settings -- Location: /utils/get_settings.py! Is this server inserted in the database?")
                return

            if language == "en":
                lang = en

    await database.close()
    return lang, gmt, auto_delete_time


# ------------------------------------------------------------------------- #
# GROUPED_SETTINGS #
# ------------------------------------------------------------------------- #
# Get language and auto_delete_time settings of a server
async def get_language_auto_delete_time_settings(guild_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_lang_auto_delete_time_settings = f'SELECT language, auto_delete_time FROM "Settings" WHERE guild_id = {guild_id}'
            fetched_lang_auto_delete_time_settings = await conn.fetch(select_lang_auto_delete_time_settings)
            
            try:
                language = fetched_lang_auto_delete_time_settings[0].get("language")
                auto_delete_time = int(fetched_lang_auto_delete_time_settings[0].get("auto_delete_time"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_language_auto_delete_time_settings -- Location: /utils/get_settings.py! Is this server inserted in the database?")
                return

            if language == "en":
                lang = en

    await database.close()
    return lang, auto_delete_time


# ------------------------------------------------------------------------- #
# INDIVIDUAL SETTINGS #
# ------------------------------------------------------------------------- #
# Get language setting of a server
async def get_language_settings(guild_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_language_setting = f'SELECT language FROM "Settings" WHERE guild_id = {guild_id}'
            fetched_language_setting = await conn.fetch(select_language_setting)
            
            try:
                language = fetched_language_setting[0].get("language")
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_language_settings -- Location: /utils/get_settings.py! Is this server inserted in the database?")
                return

            if language == "en":
                lang = en

    await database.close()
    return lang

# Get GMT setting of a server
async def get_gmt_settings(guild_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_gmt_setting = f'SELECT gmt FROM "Settings" WHERE guild_id = {guild_id}'
            fetched_gmt_setting = await conn.fetch(select_gmt_setting)
            
            try:
                gmt = fetched_gmt_setting[0].get("gmt")
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_gmt_settings -- Location: /utils/get_settings.py! Is this server inserted in the database?")
                return

    await database.close()
    return gmt

# Get auto_delete_time setting of a server
async def get_auto_delete_time_settings(guild_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_auto_delete_time_setting = f'SELECT auto_delete_time FROM "Settings" WHERE guild_id = {guild_id}'
            fetched_auto_delete_time_setting = await conn.fetch(select_auto_delete_time_setting)
            
            try:
                auto_delete_time = int(fetched_auto_delete_time_setting[0].get("auto_delete_time"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_auto_delete_time_settings -- Location: /utils/get_settings.py! Is this server inserted in the database?")
                return

    await database.close()
    return auto_delete_time