# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import os

import tanjun
from dotenv import load_dotenv
from extentions.interactions.settings.settings_logging_update import (
    command_settings_update_logging,
)
from extentions.interactions.settings.settings_update import (
    command_settings_update_general,
)
from extentions.interactions.settings.settings_update import (
    command_settings_update_raid,
)

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# THE BOTS SUB COMMANDS GROUP (E.G. /{sub_command_group}) #
# ------------------------------------------------------------------------- #
settings_update_group = (
    tanjun.slash_command_group("update", ".")
    .add_command(command_settings_update_general)
    .add_command(command_settings_update_raid)
    .add_command(command_settings_update_logging)
)
settings_group = tanjun.slash_command_group("settings", ".").add_command(settings_update_group)
