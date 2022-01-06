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