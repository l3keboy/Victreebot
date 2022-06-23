# IMPORTS
import os

import hikari
import tanjun
from core.bot import Bot
from dotenv import load_dotenv
from utils.DatabaseHandler import DatabaseHandler
from utils.helpers.BotUtils import BotUtils

load_dotenv()
BOT_NAME = os.getenv("BOT_NAME")


async def event_stopping_raid(
    event: hikari.StoppingEvent,
    db: DatabaseHandler = tanjun.injected(type=DatabaseHandler),
    bot: BotUtils = tanjun.injected(type=BotUtils),
    bot_aware: Bot = tanjun.injected(type=Bot),
):
    if bot_aware.raids != []:
        for raid in bot_aware.raids:
            raid_id = raid.strip("'")
            raid = bot_aware.raids.get(f"'{raid_id}'")

            parameters = []
            if raid.instinct_present != []:
                parameters.append(
                    f"""instinct_present = '{",".join(str(instinct) for instinct in raid.instinct_present)}'"""
                )
            else:
                parameters.append("""instinct_present = NULL""")
            if raid.mystic_present != []:
                parameters.append(f"""mystic_present = '{",".join(str(mystic) for mystic in raid.mystic_present)}'""")
            else:
                parameters.append("""mystic_present = NULL""")
            if raid.valor_present != []:
                parameters.append(f"""valor_present = '{",".join(str(valor) for valor in raid.valor_present)}'""")
            else:
                parameters.append("""valor_present = NULL""")
            if raid.remote_present != []:
                parameters.append(f"""remote_present = '{",".join(str(remote) for remote in raid.remote_present)}'""")
            else:
                parameters.append("""remote_present = NULL""")

            parameters.append(f"total_attendees = {raid.total_attendess}")

            await bot_aware.db.set_raid_detail(raid.guild, raid.raid_id, parameters=parameters)
