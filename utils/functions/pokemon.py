# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #
# IMPORTS
# Functionality
import asyncio
import pokebase as pb
# Own Files
from utils import LoggingHandler
from utils.config import const

# Get image/icon of pokemon
async def get_pokemon_img(boss):
    try:
        pokemon = pb.pokemon(str(boss.lower()))
        pokemon.id
        success=True
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_validator.error(f"Invalid pokemon {boss.lower()}!")
        success=False 
        
    if success:
        poke_img = pb.SpriteResource('pokemon', pokemon.id).url
    else:
        poke_img = None
    
    return success, poke_img


# Battle Options checker
async def battle_options(raid_tier, weather, attack_strategy, dodge_strategy, friend_level):
    raid_tier_return = const.RAID_TIERS.get(raid_tier)
    weather_return = const.WEATHERS.get(weather)
    attack_strategy_return = const.ATTACK_STRATS.get(attack_strategy)
    dodge_strategy_return = const.DODGE_STRATS.get(dodge_strategy)
    friend_level_return = const.FRIEND_LEVELS.get(friend_level)

    return raid_tier_return, weather_return, attack_strategy_return, dodge_strategy_return, friend_level_return