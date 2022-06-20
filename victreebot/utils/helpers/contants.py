# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
from languages import en

# ------------------------------------------------------------------------- #
# DEFAULT DATABASE VALUES #
# ------------------------------------------------------------------------- #
DB_GUILD_SETTINGS_DEFAUTS = {
    "language": "'en'",
    "gmt": "'GMT+0'",
    "unit_system": "'Metric System'",
    "auto_delete": "5",
    "raids_channel_id": "NULL",
    "is_setup": "false",
    "moderator_role_id": "NULL",
    "instinct_role_id": "NULL",
    "mystic_role_id": "NULL",
    "valor_role_id": "NULL",
    "instinct_emoji_id": "NULL",
    "mystic_emoji_id": "NULL",
    "valor_emoji_id": "NULL",
}
DB_GUILD_LOG_SETTINGS_GENERAL_EVENTS = {
    "logs_channel_id": "NULL",
    "log_errors": "True",
    "log_info": "True",
    "log_settings_changed": "True",
}
DB_GUILD_LOG_SETTINGS_PROFILE_EVENTS = {
    "log_profile_edit": "True",
    "log_profile_view": "True",
}
DB_GUILD_LOG_SETTINGS_LOCATION_EVENTS = {
    "log_location_add": "True",
    "log_location_delete": "True",
    "log_location_edit": "True",
    "log_location_info": "True",
    "log_location_list": "True",
}

DB_USER_DETAILS_DEFAULT = {
    "friend_codes": "NULL",
    "active_locations": "NULL",
    "stats_raids_created": "0",
    "stats_raids_participated": "0",
}
DB_GUILD_STATS_DETAILS_DEFAULT = {
    "raids_completed": "0",
    "raids_deleted": "0",
    "raids_created": "0",
}
DB_LOCATION_DETAILS_DEFAULT = {
    "type": "NULL",
    "name": "NULL",
    "latitude": "NULL",
    "longitude": "NULL",
    "description": "NULL",
}
DB_RAIDS_DETAILS_DEFAULT = {
    "raid_id": "NULL",
    "raid_type": "NULL",
    "location_type": "NULL",
    "location_name": "NULL",
    "takes_place_at": "NULL",
    "boss": "NULL",
    "end_time": "NULL",
    "instinct_present": "NULL",
    "mystic_present": "NULL",
    "valor_present": "NULL",
    "remote_present": "NULL",
    "total_attendees": "0",
    "raid_message_channel_id": "NULL",
    "raid_message_id": "NULL",
    "raid_creator_id": "NULL",
}

# ------------------------------------------------------------------------- #
# SETTINGS VALUES #
# ------------------------------------------------------------------------- #
SUPPORTED_LANGUAGES = {
    "en": en,
}
SUPPORTED_TIMEZONES = [
    "GMT-12",
    "GMT-11",
    "GMT-10",
    "GMT-9",
    "GMT-8",
    "GMT-7",
    "GMT-6",
    "GMT-5",
    "GMT-4",
    "GMT-3",
    "GMT-2",
    "GMT-1",
    "GMT+0",
    "GMT+1",
    "GMT+2",
    "GMT+3",
    "GMT+4",
    "GMT+5",
    "GMT+6",
    "GMT+7",
    "GMT+8",
    "GMT+9",
    "GMT+10",
    "GMT+11",
    "GMT+12",
]
SUPPORTED_UNIT_SYSTEMS = ["Metric System", "Imperial System", "United States Customary Unit System"]
SUPPORTED_RAID_TYPES = ["Raid", "EX-Raid", "Mega-Raid"]
SUPPORTED_LOCATION_TYPES = ["Gym", "Pokéstop"]