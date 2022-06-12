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
from extentions.interactions.profile.edit import command_profile_edit
from extentions.interactions.profile.view import command_profile_view

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# THE BOTS SUB COMMANDS GROUP (E.G. /{sub_command_group}) #
# ------------------------------------------------------------------------- #
profile_group = (
    tanjun.slash_command_group("profile", ".")
    .add_command(command_profile_edit)
    .add_command(command_profile_view)
)
