# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
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
        self.logger_victreebot_join_handler = logging.getLogger("victreebot.handlers.join")
        self.logger_victreebot_validator = logging.getLogger("victreebot.validator")
        self.logger_victreebot_stats = logging.getLogger("victreebot.stats")
        self.logger_victreebot_logger = logging.getLogger("victreebot.logger")
        self.logger_victreebot_raid_channel = logging.getLogger("victreebot.raid_channel")
        self.logger_victreebot_database = logging.getLogger("victreebot.database")
        self.logger_victreebot_update = logging.getLogger("victreebot.update")
        self.logger_victreebot_active_servers = logging.getLogger("victreebot.active_servers")
        # APSCHEDULER LOGGERS
        self.logger_apscheduler = logging.getLogger("apscheduler.scheduler")