# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import logging
import os
import sys
import typing as t

import hikari
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from utils.VersionHandler import VersionHandler

from .client import Client

clear, back_slash = "clear", "/"
if os.name == "nt":
    clear, back_slash = "cls", "\\"

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_NAME")
SUPPORT_SERVER_ID = os.getenv("SUPPORT_SERVER_ID")

_VictreeBot = t.TypeVar("_VictreeBot", bound="Bot")


# ------------------------------------------------------------------------- #
# BOT CLASS #
# ------------------------------------------------------------------------- #
class Bot(hikari.GatewayBot):
    def __init__(self) -> None:
        """Initialize hikari.GatewayBot component"""
        super().__init__(token=BOT_TOKEN, intents=hikari.Intents.ALL, banner=None)
        self.vs = VersionHandler

    def create_client(self: _VictreeBot) -> None:
        """Build a tanjun client"""
        self.client = Client.from_gateway_bot(self, declare_global_commands=True)
        self.client.load_modules()
        self.client.set_auto_defer_after(0)

    def run(self) -> None:
        """Run the Bot"""
        self.create_client()
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        super().run()

    # FUNCTIONS
    def restart(self):
        os.system(clear)
        sys.stdout.flush()
        os.execv(sys.executable, ["python"] + sys.argv)

    async def check_for_updates(self):
        logging.getLogger(f"{BOT_NAME.lower()}.update").info("Checking for updates.....")
        if not self.vs().is_latest:
            logging.getLogger(f"{BOT_NAME.lower()}.update").info("Update found! Starting update.....")
            self.vs().update_version()
            self.restart()
        logging.getLogger(f"{BOT_NAME.lower()}.update").info("No updates found!")

    # EVENT HANDLERS
    async def on_starting(self, event: hikari.StartingEvent):
        """Handle the hikari.StartingEvent"""
        # Check for updates and schedule the updates checker
        await self.check_for_updates()
        scheduler_update = AsyncIOScheduler()
        scheduler_update.add_job(self.check_for_updates, "cron", day_of_week="mon-sun", hour=3)
        scheduler_update.start()

    async def on_started(self, event: hikari.StartedEvent):
        """Handle the hikari.StartedEvent"""

    async def on_stopping(self, event: hikari.StoppingEvent):
        """Handle the hikari.StoppingEvent"""
