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
async def battle_options(weather, attack_strategy, dodge_strategy, friend_level):
    WEATHERS = {
        'Extreme': 'NO_WEATHER', 
        'Sunny/Clear': 'CLEAR', 
        'Rainy': 'RAINY', 
        'Partly Clouded': 'PARTLY_CLOUDY', 
        'Cloudy': 'OVERCAST', 
        'Windy': 'WINDY',
        'Snow': 'SNOW',
        'Fog': 'FOG' }
    ATTACK_STRATS = {
        'No Doding': 'CINEMATIC_ATTACK_WHEN_POSSIBLE', 
        'Dodge Specials PRO': 'DODGE_SPECIALS', 
        'Dodge All Weave': 'DODGE_WEAVE_CAUTIOUS'}
    DODGE_STRATS = {
        'Perfect Dodging': 'DODGE_100', 
        'Realistic Dodging': 'DODGE_REACTION_TIME', 
        'Realistic Dodging PRO': 'DODGE_REACTION_TIME2', 
        '25% Dodging': 'DODGE_25'}
    FRIEND_LEVELS = {
        'Not Friends': 'FRIENDSHIP_LEVEL_0', 
        'Good Friends': 'FRIENDSHIP_LEVEL_1', 
        'Great Friends': 'FRIENDSHIP_LEVEL_2',
        'Ultra Friends': 'FRIENDSHIP_LEVEL_3', 
        'Best Friends': 'FRIENDSHIP_LEVEL_4'}

    weather = WEATHERS.get(weather)
    attack_strategy = ATTACK_STRATS.get(attack_strategy)
    dodge_strategy = DODGE_STRATS.get(dodge_strategy)
    friend_level = FRIEND_LEVELS.get(friend_level)

    return weather, attack_strategy, dodge_strategy, friend_level