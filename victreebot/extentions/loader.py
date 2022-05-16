# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
# Hikari
# Database and .env
import os

import tanjun
from dotenv import load_dotenv

# Command Groups
# Events


load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")

# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
bot_component = (
    tanjun.Component()
    # COMMANDS
    # EVENTS
)


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(bot_component.copy())
