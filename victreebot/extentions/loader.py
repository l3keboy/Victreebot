# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
# Hikari
import hikari
import tanjun
# Database and .env
import os
from dotenv import load_dotenv
# Command Groups
from extentions.settings import settings_group, log_settings_group
# Events


load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")

# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
bot_component = (
    tanjun.Component()
    # COMMANDS
    ## Settings
    .add_command(settings_group)
    .add_command(log_settings_group)
    # EVENTS
)

@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(bot_component.copy())
