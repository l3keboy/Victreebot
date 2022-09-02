# IMPORTS
# Logging
import logging

# Functionality
import typing as t
from pathlib import Path

# Hikari
import hikari
import tanjun

_ClientT = t.TypeVar("_ClientT", bound="Client")


# ------------------------------------------------------------------------- #
# CLIENT CLASS #
# ------------------------------------------------------------------------- #
class Client(tanjun.Client):
    __slots__ = tanjun.Client.__slots__ + ("scheduler",)

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Initialize tanjun client component"""
        super().__init__(*args, **kwargs)

    def load_modules(self: _ClientT) -> _ClientT:
        """Load modules/commands from the ./victreebot/extentions folder"""
        path = Path("../Victreebot/victreebot/extentions/loader.py")

        super().load_modules(path)

        logging.getLogger("hikari.tanjun.clients").info("Modules loading complete!")
        return self

    @classmethod
    def from_gateway_bot(
        cls,
        bot: hikari.GatewayBotAware,
        /,
        *,
        event_managed: bool = True,
        mention_prefix: bool = False,
        declare_global_commands: t.Union[hikari.Snowflake, bool] = False,
    ) -> "Client":
        """Build a Client from a hikari.traits.GatewayBotAware instance"""
        constructor: Client = (
            cls(
                rest=bot.rest,
                cache=bot.cache,
                events=bot.event_manager,
                shards=bot,
                event_managed=event_managed,
                mention_prefix=mention_prefix,
                declare_global_commands=declare_global_commands,
            )
            .set_human_only()
            .set_hikari_trait_injectors(bot)
        )
        return constructor
