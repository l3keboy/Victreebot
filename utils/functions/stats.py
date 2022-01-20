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
# ALL SERVER STATS #
# ------------------------------------------------------------------------- #
# Get all stats of a server
async def get_all_server_stats(guild_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_all_server_stats = f'SELECT * FROM "ServerStats" WHERE guild_id = {guild_id}'
            fetched_all_server_stats = await conn.fetch(select_all_server_stats)
            
            try:
                stats_raids_created = int(fetched_all_server_stats[0].get("stats_raids_created"))
                stats_raids_deleted = int(fetched_all_server_stats[0].get("stats_raids_deleted"))
                stats_raids_completed = int(fetched_all_server_stats[0].get("stats_raids_completed"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_all_server_stats -- Location: /utils/get_stats.py! Is this server inserted in the database?")
                await database.close()
                return

    await database.close()
    return stats_raids_created, stats_raids_deleted, stats_raids_completed


# ------------------------------------------------------------------------- #
# INDIVIDUAL SERVER STATS #
# ------------------------------------------------------------------------- #
# Get stats_raids_created of a server
async def get_server_raids_created(guild_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_server_raids_created = f'SELECT stats_raids_created FROM "ServerStats" WHERE guild_id = {guild_id}'
            fetched_server_raids_created = await conn.fetch(select_server_raids_created)
            
            try:
                stats_raids_created = int(fetched_server_raids_created[0].get("stats_raids_created"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_server_raids_created -- Location: /utils/get_stats.py! Is this server inserted in the database?")
                await database.close()
                return

    await database.close()
    return stats_raids_created

# Get stats_raids_deleted of a server
async def get_server_raids_deleted(guild_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_server_raids_deleted = f'SELECT stats_raids_deleted FROM "ServerStats" WHERE guild_id = {guild_id}'
            fetched_server_raids_deleted = await conn.fetch(select_server_raids_deleted)
            
            try:
                stats_raids_deleted = int(fetched_server_raids_deleted[0].get("stats_raids_deleted"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_server_raids_deleted -- Location: /utils/get_stats.py! Is this server inserted in the database?")
                await database.close()
                return

    await database.close()
    return stats_raids_deleted

# Get stats_raids_completed of a server
async def get_server_raids_completed(guild_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_server_raids_completed = f'SELECT stats_raids_deleted FROM "ServerStats" WHERE guild_id = {guild_id}'
            fetched_server_raids_completed = await conn.fetch(select_server_raids_completed)
            
            try:
                stats_raids_completed = int(fetched_server_raids_completed[0].get("stats_raids_completed"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_server_raids_completed -- Location: /utils/get_stats.py! Is this server inserted in the database?")
                await database.close()
                return

    await database.close()
    return stats_raids_completed


# ------------------------------------------------------------------------- #
# ALL USER STATS #
# ------------------------------------------------------------------------- #
# Get all stats of a user
async def get_all_user_stats(guild_id, user_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_all_user_stats = f'SELECT stats_raids_created, stats_raids_participated FROM "{guild_id}" WHERE user_id = {user_id}'
            fetched_all_user_stats = await conn.fetch(select_all_user_stats)
            
            try:
                stats_raids_created = int(fetched_all_user_stats[0].get("stats_raids_created"))
                stats_raids_participated = int(fetched_all_user_stats[0].get("stats_raids_participated"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_all_user_stats -- Location: /utils/get_stats.py! Is this server and/or user inserted in the database?")
                await database.close()
                return

    await database.close()
    return stats_raids_created, stats_raids_participated


# ------------------------------------------------------------------------- #
# INDIVIDUAL USER STATS #
# ------------------------------------------------------------------------- #
# Get stats_raids_created of a user
async def get_user_raids_created(guild_id, user_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_user_raids_created = f'SELECT stats_raids_created FROM "{guild_id}" WHERE user_id = {user_id}'
            fetched_user_raids_created = await conn.fetch(select_user_raids_created)
            
            try:
                stats_raids_created = int(fetched_user_raids_created[0].get("stats_raids_created"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_user_raids_created -- Location: /utils/get_stats.py! Is this server inserted in the database?")
                await database.close()
                return

    await database.close()
    return stats_raids_created

# Get stats_raids_participated of a user
async def get_user_raids_participated(guild_id, user_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            select_user_raids_participated = f'SELECT stats_raids_participated FROM "{guild_id}" WHERE user_id = {user_id}'
            fetched_user_raids_participated = await conn.fetch(select_user_raids_participated)
            
            try:
                stats_raids_participated = int(fetched_user_raids_participated[0].get("stats_raids_participated"))
            except IndexError as e:
                LoggingHandler().logger_victreebot_database.error(f"Index error. Guild_id: {guild_id} -- Function: get_user_raids_participated -- Location: /utils/get_stats.py! Is this server inserted in the database?")
                await database.close()
                return

    await database.close()
    return stats_raids_participated


# ------------------------------------------------------------------------- #
# UPDATE STATS #
# ------------------------------------------------------------------------- #
async def update_server_stats(guild_id, stat, add: bool = True):
    # GET ALL CURRENT SERVER STATS
    stats_raids_created, stats_raids_deleted, stats_raids_completed = await get_all_server_stats(guild_id=guild_id)
    STATS = {
        "stats_raids_created": stats_raids_created,
        "stats_raids_deleted": stats_raids_deleted,
        "stats_raids_completed": stats_raids_completed
    }

    # UPDATE THE STAT
    if add:
        updated_stat = STATS.get(stat) + 1
    else:
        updated_stat = STATS.get(stat) - 1
        if updated_stat < 0:
            updated_stat = 0

    # UPDATE SERVERSTATS
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                update_server_stat = f'UPDATE "ServerStats" SET {stat} = {updated_stat} WHERE guild_id = {guild_id}'
                await conn.fetch(update_server_stat)
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while trying to update {stat} for guild_id: {guild_id}! Got error: {e}")
    await database.close()


async def update_user_stats(guild_id, user_id, stat, add: bool = True):
    # GET ALL CURRENT USER STATS
    stats_raids_created, stats_raids_participated = await get_all_user_stats(guild_id=guild_id, user_id=user_id)
    STATS = {
        "stats_raids_created": stats_raids_created,
        "stats_raids_participated": stats_raids_participated,
    }

    # UPDATE THE STAT
    if add:
        updated_stat = STATS.get(stat) + 1
    else:
        updated_stat = STATS.get(stat) - 1
        if updated_stat < 0:
            updated_stat = 0

    # UPDATE USERSTATS
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            try:
                update_server_stat = f'UPDATE "{guild_id}" SET {stat} = {updated_stat} WHERE user_id = {user_id}'
                await conn.fetch(update_server_stat)
            except Exception as e:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Something went wrong while trying to update {stat} for user_id: {user_id} in guild_id: {guild_id}! Got error: {e}")
    await database.close()