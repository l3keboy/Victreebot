# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import os

import hikari
import tanjun
from dotenv import load_dotenv
from extentions.events.guild_join_setup import event_guild_join_setup
from extentions.events.guild_leave_remove import event_guild_leave_remove
from extentions.events.member_create_add import event_member_create_add
from extentions.events.member_delete_remove import event_member_delete_remove
from extentions.interactions.locations.locations import command_locations
from extentions.interactions.profile import profile_group
from extentions.interactions.setup.setup import command_setup
from extentions.interactions.setup.reset import command_reset

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")

# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
bot_component = (
    tanjun.Component()
    # EVENTS
    .add_listener(hikari.GuildJoinEvent, event_guild_join_setup)
    .add_listener(hikari.GuildLeaveEvent, event_guild_leave_remove)
    .add_listener(hikari.MemberCreateEvent, event_member_create_add)
    .add_listener(hikari.MemberDeleteEvent, event_member_delete_remove)
    # INTERACTIONS
    .add_command(command_setup)
    .add_command(command_reset)
    .add_command(profile_group)
    .add_command(command_locations)
)


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(bot_component.copy())
