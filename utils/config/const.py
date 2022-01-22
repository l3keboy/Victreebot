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

# ------------------------------------------------------------------------- #
# FUNCTION CONSTANTS #
# ------------------------------------------------------------------------- #
RAID_TIERS={
    "Level 1": "RAID_LEVEL_1",
    "Level 2": "RAID_LEVEL_2",
    "Level 3": "RAID_LEVEL_3",
    "Level 4": "RAID_LEVEL_4",
    "Level 5": "RAID_LEVEL_5",
    "Level 6": "RAID_LEVEL_6" 
}

WEATHERS={
    "Extreme": "NO_WEATHER", 
    "Sunny/Clear": "CLEAR", 
    "Rainy": "RAINY", 
    "Partly Clouded": "PARTLY_CLOUDY", 
    "Cloudy": "OVERCAST", 
    "Windy": "WINDY",
    "Snow": "SNOW",
    "Fog": "FOG" 
}

ATTACK_STRATS={
    "No Doding": "CINEMATIC_ATTACK_WHEN_POSSIBLE", 
    "Dodge Specials PRO": "DODGE_SPECIALS", 
    "Dodge All Weave": "DODGE_WEAVE_CAUTIOUS"
}

DODGE_STRATS={
    "Perfect Dodging": "DODGE_100", 
    "Realistic Dodging": "DODGE_REACTION_TIME", 
    "Realistic Dodging PRO": "DODGE_REACTION_TIME2", 
    "25% Dodging": "DODGE_25"
}
    
FRIEND_LEVELS={
    "Not Friends": "FRIENDSHIP_LEVEL_0", 
    "Good Friends": "FRIENDSHIP_LEVEL_1", 
    "Great Friends": "FRIENDSHIP_LEVEL_2",
    "Ultra Friends": "FRIENDSHIP_LEVEL_3", 
    "Best Friends": "FRIENDSHIP_LEVEL_4"
}