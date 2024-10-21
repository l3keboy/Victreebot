# IMPORTS
import asyncio
import logging
import os
from itertools import cycle

import hikari
from dotenv import load_dotenv

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


# ------------------------------------------------------------------------- #
# ACTIVITYHANDLER CLASS #
# ------------------------------------------------------------------------- #
class ActivityHandler:
    """Set cycling activities for the bot, see on_started event!"""

    def __init__(self, bot) -> None:
        self.bot = bot

    async def _init(self):
        self._activities = cycle(
            [
                hikari.Activity(
                    type=hikari.ActivityType.COMPETING,
                    name="Pokémon GO!",
                ),
                hikari.Activity(
                    type=hikari.ActivityType.PLAYING,
                    name=f"{self.bot.version}",
                ),
                hikari.Activity(
                    type=hikari.ActivityType.WATCHING,
                    name="Pokémon",
                ),
            ]
        )

    async def change_activity(self) -> None:
        """Function that changes to bots activity every 30 minutes"""
        logging.getLogger(f"{BOT_NAME.lower()}.activity").info("Starting ActivityHandler.....")
        try:
            while True:
                logging.getLogger(f"{BOT_NAME.lower()}.activity").info("Changing activity.....")
                new_presence = next(self._activities)
                await self.bot.update_presence(activity=new_presence, status=hikari.Status.ONLINE)
                await asyncio.sleep(1800)
        except Exception as e:
            logging.getLogger(f"{BOT_NAME.lower()}.activity").info(
                f"Error while starting ActivityHandler! Got error: {e}"
            )
