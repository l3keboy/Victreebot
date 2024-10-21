# IMPORTS
import os
import logging
import typing as t
import requests

import hikari
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from utils.ActivityHandler import ActivityHandler
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils

from .client import Client

clear, back_slash = "clear", "/"
if os.name == "nt":
    clear, back_slash = "cls", "\\"

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_NAME")
SUPPORT_SERVER_ID = os.getenv("SUPPORT_SERVER_ID")
API_BEARER_GITHUB = os.getenv("API_BEARER_GITHUB")
API_RELEASE_URL_GITHUB = os.getenv("API_RELEASE_URL_GITHUB")

_VictreeBot = t.TypeVar("_VictreeBot", bound="Bot")


# ------------------------------------------------------------------------- #
# BOT CLASS #
# ------------------------------------------------------------------------- #
class Bot(hikari.GatewayBot):
    def __init__(self) -> None:
        """Initialize hikari.GatewayBot component"""
        super().__init__(token=BOT_TOKEN, intents=hikari.Intents.ALL, banner=None)
        self.version = "Latest Version"

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
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_stopped)
        super().run()

    # FUNCTIONS
    def check_latest_version(self) -> str:
        """Function to check the latest version number on GitHub Repo"""
        logging.getLogger(f"{BOT_NAME.lower()}.core.version").info("Checking latest version number.....!")
        version = "Latest Version"
        try:
            headers = {"Authorization": "Bearer " + API_BEARER_GITHUB}
            response = requests.get(url=API_RELEASE_URL_GITHUB, headers=headers)
            response = response.json()
            version = response["tag_name"]
            logging.getLogger(f"{BOT_NAME.lower()}.core.version").info(
                f"Found latest version, continuing with: '{version}'!"
            )
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.core.version").error(
                "Checking latest version number failed, continuing with: 'Latest Version'! " f"Got error: {e}"
            )
        self.version = version
        return version

    # EVENT HANDLERS
    async def on_starting(self, event: hikari.StartingEvent):
        """Handle the hikari.StartingEvent"""
        self.check_latest_version()
        # Init DatabaseHandler, create database pool and inject
        self.db = DatabaseHandler()
        await self.db.connect()
        self.client.set_type_dependency(DatabaseHandler, self.db)

        # Inject BotUtils
        self.client.set_type_dependency(BotUtils, BotUtils())

    async def on_started(self, event: hikari.StartedEvent):
        """Handle the hikari.StartedEvent"""
        # Init ActivityHandler, set activity
        self.ah = ActivityHandler(self)
        await self.ah._init()
        await self.ah.change_activity()

        # Inject RESTAware bot object
        self.client.set_type_dependency(Bot, self)

    async def on_stopped(self, event: hikari.StoppedEvent):
        """Handle the hikari.StoppingEvent"""
        # Close database pool
        await self.db.close()
