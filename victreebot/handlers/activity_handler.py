# Copyright (c) 2022-present l3keboy

# IMPORTS
from __future__ import annotations

import asyncio
import logging
from itertools import cycle
from typing import TYPE_CHECKING

import hikari

if TYPE_CHECKING:
    from victreebot.core.bot import Bot


# ------------------------------------------------------------------------- #
# ACTIVITY HANDLER CLASS #
# ------------------------------------------------------------------------- #
class ActivityHandler:
    """Cycle activities for the bot, see on_started event."""

    def __init__(self, bot: Bot) -> None:
        """Init ActivityHandler."""
        self.bot = bot

    async def setup_activities(self) -> None:
        """FetCH the statuses and the variables for in the statuses."""
        logging.getLogger(__name__).info("Renewing activities.....")

        # Create a list of all activities to display
        self._activities = [
            hikari.Activity(type=hikari.ActivityType.COMPETING, name="Pokémon GO!"),
            hikari.Activity(type=hikari.ActivityType.PLAYING, name=f"{self.bot.version}"),
            hikari.Activity(type=hikari.ActivityType.WATCHING, name="Pokémon"),
        ]

        # Create iterable activities cycle
        self._activities_cycle = cycle(self._activities)

    async def change_activity(self) -> None:
        """Change the bots activity every 30 minutes."""
        logging.getLogger(__name__).info("Starting ActivityHandler.....")
        try:
            i = 0
            while True:
                logging.getLogger(__name__).info("Changing activity!")
                # Check if the statusses has been looped fully
                if i < len(self._activities):
                    # If statusses are not fully looped, continue with next status
                    i += 1
                    new_presence = next(self._activities_cycle)
                else:
                    # If statusses are fully looped, refresh statusses
                    i = 0
                    await self.setup_activities()
                    new_presence = next(self._activities_cycle)

                # Update the bots presence and wait till next update time
                await self.bot.update_presence(activity=new_presence, status=hikari.Status.ONLINE)
                await asyncio.sleep(1800)
        except Exception:
            logging.getLogger(__name__).exception("Error while executing ActivityHandler!")
