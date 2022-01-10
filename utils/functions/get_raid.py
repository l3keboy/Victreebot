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


# Get a raid by its raid_id
async def get_raid_by_raidid_raidtype(search_raid_type, search_raid_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            id_to_get = "'" + str(search_raid_id) + "'" 
            type_to_get = "'" + search_raid_type + "'"
            get_raid = f'SELECT * FROM "Raid-Events" WHERE type = {type_to_get} AND id = {id_to_get}'
            fetched_raid = await conn.fetch(get_raid)

            if fetched_raid == []:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Tried to fetch raid by ID with ID that does not exist!")
                success = False
                raid_id, created_at, raid_type, guild_id, channel_id, message_id, user_id, boss, location, time, date, instinct_present, mystic_present, valor_present, remote_present, total_attendees = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            else:
                success = True
                raid_id = fetched_raid[0].get("id")
                created_at = fetched_raid[0].get("created_at")
                raid_type = fetched_raid[0].get("type")
                guild_id = fetched_raid[0].get("guild_id")
                channel_id = fetched_raid[0].get("channel_id")
                message_id = fetched_raid[0].get("message_id")
                user_id = fetched_raid[0].get("user_id")
                boss = fetched_raid[0].get("boss")
                location = fetched_raid[0].get("location")
                time = fetched_raid[0].get("time")
                date = fetched_raid[0].get("date")
                instinct_present = fetched_raid[0].get("instinct_present")
                mystic_present = fetched_raid[0].get("mystic_present")
                valor_present = fetched_raid[0].get("valor_present")
                remote_present = fetched_raid[0].get("remote_present")
                total_attendees = fetched_raid[0].get("total_attendees")
    await database.close()

    return success, raid_id, created_at, raid_type, guild_id, channel_id, message_id, user_id, boss, location, time, date, instinct_present, mystic_present, valor_present, remote_present, total_attendees


# Get a raid by its raid_id
async def get_raid_by_guild_channel_message(guild_id, channel_id, message_id):
    database = await DatabaseHandler.acquire_database()
    async with database.acquire() as conn:
        async with conn.transaction():
            get_raid = f'SELECT * FROM "Raid-Events" WHERE guild_id = {guild_id} AND channel_id = {channel_id} AND message_id = {message_id}'
            fetched_raid = await conn.fetch(get_raid)

            if fetched_raid == []:
                LoggingHandler.LoggingHandler().logger_victreebot_database.error(f"Tried to fetch raid by guild, channel and message that does not exist!")
                success = False
                raid_id, created_at, raid_type, guild_id, channel_id, message_id, user_id, boss, location, time, date, instinct_present, mystic_present, valor_present, remote_present, total_attendees = None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            else:
                success = True
                raid_id = fetched_raid[0].get("id")
                created_at = fetched_raid[0].get("created_at")
                raid_type = fetched_raid[0].get("type")
                guild_id = fetched_raid[0].get("guild_id")
                channel_id = fetched_raid[0].get("channel_id")
                message_id = fetched_raid[0].get("message_id")
                user_id = fetched_raid[0].get("user_id")
                boss = fetched_raid[0].get("boss")
                location = fetched_raid[0].get("location")
                time = fetched_raid[0].get("time")
                date = fetched_raid[0].get("date")
                instinct_present = fetched_raid[0].get("instinct_present")
                mystic_present = fetched_raid[0].get("mystic_present")
                valor_present = fetched_raid[0].get("valor_present")
                remote_present = fetched_raid[0].get("remote_present")
                total_attendees = fetched_raid[0].get("total_attendees")
    await database.close()

    return success, raid_id, created_at, raid_type, guild_id, channel_id, message_id, user_id, boss, location, time, date, instinct_present, mystic_present, valor_present, remote_present, total_attendees