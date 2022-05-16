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
}
DB_GUILD_LOG_SETTINGS_GENERAL_EVENTS = {
    "log_errors": "True",
    "log_info": "True",
    "log_settings_changed": "True",
}

DB_USER_DEFAUTS = {
    "friendcodes": "NULL",
    "active_locations": "NULL",
    "stats_raids_created": "0",
    "stats_raids_participated": "0",
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
