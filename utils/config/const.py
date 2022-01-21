# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #
# IMPORTS
# Own files
from language import en

# ------------------------------------------------------------------------- #
# COMMAND CONSTANTS #
# ------------------------------------------------------------------------- #
# 1_settings
SUPPORTED_LANGUAGES={
    "en": en,
}

SUPPORTED_TIMEZONES=[
    "GMT-12", "GMT-11",
    "GMT-10", "GMT-9",
    "GMT-8", "GMT-7",
    "GMT-6", "GMT-5",
    "GMT-4", "GMT-3",
    "GMT-2", "GMT-1",
    "GMT+0", "GMT+1",
    "GMT+2", "GMT+3",
    "GMT+4", "GMT+5",
    "GMT+6", "GMT+7",
    "GMT+8", "GMT+9",
    "GMT+10", "GMT+11",
    "GMT+12"
]

# 2_location
LOCATION_TYPES=[
    "Gym", "Pokéstop"
]

# 3_raid
RAID_TYPES=[
    "Raid", "Mega-Raid", "EX-Raid"
]
