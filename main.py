# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #
# IMPORTS
# Database and .env
import os
from dotenv import load_dotenv
import asyncpg
# Logging
import logging
# Hikari
import hikari
import tanjun
# Functionality
from pathlib import Path
import sys
import pyfiglet
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Own Files
from utils import DatabaseHandler, LoggingHandler, VersionHandler

# .ENV and .ENV VARIABLES
# Load .env
load_dotenv()
# Variables
# Bot Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_NAME")

GUILD_ID = 438415532602032138
clear, back_slash = "clear", "/"
if os.name == "nt":
    clear, back_slash = "cls", "\\"

# ------------------------------------------------------------------------- #
# FUNCTIONS #
# ------------------------------------------------------------------------- #
def start():
    os.system(clear)
    sys.stdout.flush()
    print(pyfiglet.figlet_format(f'{BOT_NAME}') + '\n--------------------------------------------------')
    # SET LOGGERS
    LoggingHandler.LoggingHandler().logger_apscheduler.setLevel(logging.WARNING)


# ------------------------------------------------------------------------- #
# BOT CLASS #
# ------------------------------------------------------------------------- #
class Bot(hikari.GatewayBot):
    def __init__(self):
        super().__init__(
            token=BOT_TOKEN,
            intents=hikari.Intents.ALL,
            banner=None,
        )
        self.vs = VersionHandler
    
    def create_client(self):
        LoggingHandler.LoggingHandler().hikari_tanjun_clients.info("Loading modules.....")
        self.client = tanjun.Client.from_gateway_bot(self, declare_global_commands=True)
        self.client.load_modules(*Path("../VictreeBot/commands").glob("*.py"))
        LoggingHandler.LoggingHandler().hikari_tanjun_clients.info("Loading Complete!\n")

    def run(self):
        self.create_client()
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        super().run(
            activity=hikari.Activity(
                name=f"pokémon",
                type=hikari.ActivityType.PLAYING,
            )
        )
    
    # FUNCTIONS
    def restart(self):
        os.system(clear)
        sys.stdout.flush()
        os.execv(sys.executable, ['python'] + sys.argv)

    async def check_for_updates(self):
        LoggingHandler.LoggingHandler().logger_victreebot_update.info(f"Checking for updates.....")
        if not self.vs.VersionHandler().is_latest:
            LoggingHandler.LoggingHandler().logger_victreebot_update.info(f"Update found! Started updating bot to the latest version.....\n")
            self.vs.VersionHandler().update_version()
            self.restart()
        LoggingHandler.LoggingHandler().logger_victreebot_update.info(f"No updates found! Starting {self.vs.VersionHandler().version_full} of {BOT_NAME} normally!\n")

    async def get_active_servers(self, event):
        LoggingHandler.LoggingHandler().logger_victreebot_active_servers.info(f"Checking for the number of active servers.....")
        guilds = await event.app.rest.fetch_my_guilds()
        active_guilds = len(guilds)
        database = await DatabaseHandler.acquire_database()
        async with database.acquire() as conn:
            async with conn.transaction():
                try:
                    active_server_query = f'UPDATE "Settings" SET active_servers = {active_guilds}'
                    await conn.execute(active_server_query)
                except asyncpg.exceptions.UniqueViolationError:
                    pass
        await database.close()
        LoggingHandler.LoggingHandler().logger_victreebot_active_servers.info(f"Active server check complete!\n")

    # EVENT HANDLERS
    async def on_starting(self, event: hikari.StartingEvent) -> None:
        await self.check_for_updates()
        await self.get_active_servers(event)

        AsyncIOScheduler().add_job(self.check_for_updates, 'cron', day_of_week='mon-sun', hour=3)
        AsyncIOScheduler().add_job(self.get_active_servers, 'interval', [event], hours=6)
        AsyncIOScheduler().start()


# ------------------------------------------------------------------------- #
# INITIALIZE #
# ------------------------------------------------------------------------- #
if __name__ == "__main__":
    try:
        if os.name != "nt":
            import uvloop
            uvloop.install()

        start()
        Bot().run()
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_apscheduler.error(f"An error occured while starting:\n{e}")
