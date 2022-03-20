# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
# Hikari
import tanjun
# Database and .env
import os
from dotenv import load_dotenv
# Commands
from extentions.settings.settings import *
from extentions.settings.log_settings import *


load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")

# ------------------------------------------------------------------------- #
# THE BOTS SUB COMMANDS GROUP (E.G. /{sub_command_group}) #
# ------------------------------------------------------------------------- #
settings_update_group=(
    tanjun.slash_command_group("update", f"Update settings.")
    .add_command(command_settings_update_raids_channel)
    .add_command(command_settings_update_general)
)
settings_group=(
    tanjun.slash_command_group(f"settings", f"Change {BOT_NAME.capitalize()} settings.")
    .add_command(settings_update_group)
)

# ------------------------------------------------------------------------- #
# THE BOTS SUB COMMANDS GROUP (E.G. /{sub_command_group}) #
# ------------------------------------------------------------------------- #
log_settings_update_group=(
    tanjun.slash_command_group("update", f"Update log settings.")
    .add_command(command_log_settings_update_log_channel)
    .add_command(command_log_settings_update_general_events)
)
log_settings_group=(
    tanjun.slash_command_group(f"log_settings", f"Change {BOT_NAME.capitalize()} log settings.")
    .add_command(log_settings_update_group)
)