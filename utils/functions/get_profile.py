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
from utils import LoggingHandler


# ------------------------------------------------------------------------- #
# ALL PROFILE DETAILS #
# ------------------------------------------------------------------------- #
# Get all profile details of a user in a server
async def get_all_profile_details(guild_id, user_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_all_profile_details = f'SELECT * FROM "{guild_id}" WHERE user_id = {user_id}'
            fetched_all_profile_details = await conn.fetch(select_all_profile_details)
            
            try:
                friend_codes = fetched_all_profile_details[0].get("friend_codes")
                location = fetched_all_profile_details[0].get("location")
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_all_profile_details -- Location: /utils/get_profile.py! Is this server and/or user inserted in the database?")
                await database.close()
                return

    await database.close()
    return friend_codes, location


# ------------------------------------------------------------------------- #
# GROUPED PROFILE DETAILS #
# ------------------------------------------------------------------------- #


# ------------------------------------------------------------------------- #
# INDIVIDUAL PROFILE DETAILS #
# ------------------------------------------------------------------------- #
# Get friend codes of a user in a server
async def get_friend_codes(guild_id, user_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_friend_codes = f'SELECT friend_codes FROM "{guild_id}" WHERE user_id = {user_id}'
            fetched_friend_codes = await conn.fetch(select_friend_codes)
            
            try:
                friend_codes = fetched_friend_codes[0].get("friend_codes")
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_friend_codes -- Location: /utils/get_profile.py! Is this server and/or user inserted in the database?")
                await database.close()
                return

    await database.close()
    return friend_codes


# Get location of a user in a server
async def get_location(guild_id, user_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_location = f'SELECT location FROM "{guild_id}" WHERE user_id = {user_id}'
            fetched_location = await conn.fetch(select_location)
            
            try:
                location = fetched_location[0].get("location")
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_location -- Location: /utils/get_profile.py! Is this server and/or user inserted in the database?")
                await database.close()
                return

    await database.close()
    return location

