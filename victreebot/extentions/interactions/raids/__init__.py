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
from extentions.interactions.raids.create import command_raid_create
from extentions.interactions.raids.delete import command_raid_delete
from extentions.interactions.raids.edit import command_raid_edit

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# THE BOTS SUB COMMANDS GROUP (E.G. /{sub_command_group}) #
# ------------------------------------------------------------------------- #
raid_group = (
    tanjun.slash_command_group("raid", ".")
    .add_command(command_raid_create)
    .add_command(command_raid_delete)
    .add_command(command_raid_edit)
)
