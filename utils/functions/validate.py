# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #
# IMPORTS
# Database and .env
import asyncpg
# Functionality
import datetime
# Own Files
from utils import DatabaseHandler, LoggingHandler


# ------------------------------------------------------------------------- #
# LATITUDE LONGITUDE #
# ------------------------------------------------------------------------- #
# Validate latitude and longitude
async def __latitude_longitude_check(latitude, longitude):
    valid_latitude = False
    valid_longitude = False

    if latitude >= -90 and latitude <= 90:
        valid_latitude = True
    else:
        LoggingHandler.LoggingHandler().logger_victreebot_validator.error("Invalid latitude given!")
    if longitude >= -180 and longitude <=180:
        valid_longitude = True
    else:
        LoggingHandler.LoggingHandler().logger_victreebot_validator.error("Invalid longitude given!")

    return valid_latitude, valid_longitude

# ------------------------------------------------------------------------- #
# LOCATION #
# ------------------------------------------------------------------------- #
# Validate is a location exists in the database
async def __validate_location(guild_id, location):
    location_exists = False
    location_to_find = "'" + location.lower() + "'"
    try:
        database = await DatabaseHandler.acquire_database()
        async with database.acquire() as conn:
            async with conn.transaction():
                search_gym = f'SELECT latitude, longitude FROM "Gym" WHERE guild_id = {guild_id} AND name = {location_to_find}'
                fetched_locations = await conn.fetch(search_gym)
                if fetched_locations == []:
                    pass
                else:
                    location_exists = True
                    latitude = fetched_locations[0].get("latitude")
                    longitude = fetched_locations[0].get("longitude")
        await database.close()
    except asyncpg.exceptions.UndefinedColumnError:
        pass

    if not location_exists:
        try:
            database = await DatabaseHandler.acquire_database()
            async with database.acquire() as conn:
                async with conn.transaction():
                    search_gym = f'SELECT latitude, longitude FROM "Pokéstop" WHERE guild_id = {guild_id} AND name = {location_to_find}'
                    fetched_locations = await conn.fetch(search_gym)
                    if fetched_locations == []:
                        pass
                    else:
                        location_exists = True
                        latitude = fetched_locations[0].get("latitude")
                        longitude = fetched_locations[0].get("longitude")
            await database.close()
        except asyncpg.exceptions.UndefinedColumnError:
            pass

    if not location_exists:
        LoggingHandler.LoggingHandler().logger_victreebot_validator.error(f"User in guild_id {guild_id} tried to start a raid with an non existing location!")

    return location_exists, latitude, longitude

# ------------------------------------------------------------------------- #
# DATETIME #
# ------------------------------------------------------------------------- #
# Validate if the time is in the HH:MM format
async def __validate_time(time):
    try:
        datetime.datetime.strptime(time, "%H:%M")
        return True
    except ValueError:
        LoggingHandler.LoggingHandler().logger_victreebot_validator.error("Invalid time format given!")
        return False

# Validate if the date is in the DD-MM-YYYY format
async def __validate_date(date):
    try:
        datetime.datetime.strptime(date, "%d-%m-%Y")
        return True
    except ValueError:
        LoggingHandler.LoggingHandler().logger_victreebot_validator.error("Invalid date format given!")
        return False