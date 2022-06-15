# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import datetime
import logging

from colorama import Fore
from colorama import Style
from colorama import init

init()

LOG_LEVEL_COLORS_LEVEL_SECTION = {
    "DEBUG": f"{Style.BRIGHT}{Fore.CYAN}",
    "INFO": f"{Style.BRIGHT}{Fore.BLUE}",
    "WARNING": f"{Style.BRIGHT}{Fore.YELLOW}",
    "ERROR": f"{Style.BRIGHT}{Fore.LIGHTRED_EX}",
    "CRITICAL": f"{Style.NORMAL}{Fore.RED}",
}
LOG_LEVEL_COLORS_MESSAGE_SECTION = {
    "DEBUG": "",
    "INFO": "",
    "WARNING": f"{Style.BRIGHT}{Fore.YELLOW}",
    "ERROR": f"{Style.BRIGHT}{Fore.LIGHTRED_EX}",
    "CRITICAL": f"{Style.NORMAL}{Fore.RED}",
}
LOGGER_COLORS = {
    "victreebot": f"{Style.DIM}{Fore.LIGHTBLUE_EX}",
    "hikari": f"{Style.DIM}{Fore.MAGENTA}",
    "apscheduler": f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}",
    "lavalink_rs": f"{Style.BRIGHT}{Fore.CYAN}",
}


# ------------------------------------------------------------------------- #
# LOGGINGHANDLER CLASS #
# ------------------------------------------------------------------------- #
class LoggingHandler(logging.Logger):
    def handle(self, record: logging.LogRecord) -> None:
        """Handle the logging.LogRecord instance and pretty output to console"""
        name = record.name
        level_name = record.levelname
        message = record.msg
        if record.args is not None:
            message = record.msg % record.args
        exec_info = record.exc_info
        time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")

        print(
            f"{Style.NORMAL}{Fore.GREEN}{time}{Style.RESET_ALL}"
            f" | {LOG_LEVEL_COLORS_LEVEL_SECTION.get(level_name)}{level_name.center(8)}{Style.RESET_ALL} | "
            f"{self._get_logger_color(name)}{name:<60}{Style.RESET_ALL}"
            f" {LOG_LEVEL_COLORS_MESSAGE_SECTION.get(level_name)} » {message}{Style.RESET_ALL}"
        )

        if exec_info:
            print(exec_info)

    def _get_logger_color(self, name) -> str:
        """Get the color of the logger"""
        for logger_name, color in LOGGER_COLORS.items():
            if name.startswith(logger_name):
                return color
        return f"{Style.NORMAL}{Fore.WHITE}"
