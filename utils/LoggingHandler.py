# ------------------------------------------------------------------------- #
# Husqy Discord Bot, see https://www.husqy.xyz for more info                #
#                                                                           #
# Copyright (C) Husqy - All Rights Reserved                                 #
# Unauthorized copying of this file, via any medium is strictly prohibited  #
# Proprietary and confidential                                              #
# Written by Luke Hendriks <luke@la-online.nl>, July 2021 (C)               #
# ------------------------------------------------------------------------- #
# IMPORTS
# Logging
import logging


class LoggingHandler:
    def __init__(self):
        # ROOT LOGGERS
        self.logger_root = logging.getLogger("root")
        # HIKARI LOGGERS
        self.hikari_tanjun_clients = logging.getLogger("hikari.tanjun.clients")
        # HUSQY LOGGERS
        self.logger_victreebot = logging.getLogger("victreebot")
        self.logger_victreebot_database = logging.getLogger("victreebot.database")
        self.logger_victreebot_update = logging.getLogger("victreebot.update")
        self.logger_victreebot_active_servers = logging.getLogger("victreebot.active_servers")
        # APSCHEDULER LOGGERS
        self.logger_apscheduler = logging.getLogger("apscheduler.scheduler")