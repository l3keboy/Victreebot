import logging
import os
import sys

from victreebot.core.bot import Bot
from victreebot.utils.setup_opentelemetry import setup_opentelemetry

if __name__ == "__main__":
    try:
        if os.name != "nt":
            import uvloop

            uvloop.install()

        bot = Bot()
        setup_opentelemetry(bot)
        bot.run()
    except Exception:
        logging.getLogger(__name__).exception("Error while starting Victreebot!")
        sys.exit(1)