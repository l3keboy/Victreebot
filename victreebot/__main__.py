# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
# Logging
import logging

# Own Files
from utils.LoggingHandler import LoggingHandler

logging.basicConfig(level="INFO")
logging.setLoggerClass(LoggingHandler)
# Database and .env
import os

# Functionality
import sys

import pyfiglet
from core.bot import Bot
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_NAME")

clear, back_slash = "clear", "/"
if os.name == "nt":
    clear, back_slash = "cls", "\\"


def start():
    # Clear terminal
    os.system(clear)
    sys.stdout.flush()
    # Print BOT_NAME in figlet format
    print(pyfiglet.figlet_format(f"{BOT_NAME}") + "\n----------------------------------------------")


if __name__ == "__main__":
    try:
        if os.name != "nt":
            import uvloop

            uvloop.install()

        start()
        Bot().run()
    except Exception as e:
        print(e)
