# Copyright (c) 2022-present l3keboy

import asyncio
import datetime
import logging
from collections.abc import Sequence

import hikari
import lightbulb
import linkd
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from dotenv import load_dotenv
from hikari import presences

from victreebot import extensions
from victreebot.handlers.activity_handler import ActivityHandler
from victreebot.handlers.database_handler import DatabaseHandler
from victreebot.services.discord_service import DiscordService
from victreebot.utils.classes.RaidClass import RaidClass
from victreebot.utils.classes.victreebot_bot_variables import VictreeBotBotVariables
from victreebot.utils.EnvVarLoader import EnvVarLoader
from victreebot.utils.global_utils import GlobalUtils

load_dotenv()


class Bot(hikari.GatewayBot):
    """VictreeBot class for running the VictreeBot Discord bot as a Discord Gateway bot."""

    vars: VictreeBotBotVariables
    client: lightbulb.Client
    activity_handler_task: asyncio.Task[None]
    di_default_registry: linkd.Registry
    # Schedulers
    scheduler_entitlement_sync: AsyncIOScheduler
    # Handlers
    activity_handler: ActivityHandler
    database: DatabaseHandler
    # Services
    discord_service: DiscordService
    discord_cache_service: hikari.api.Cache
    # Raids
    raids: dict[str, RaidClass | None]

    # INIT
    def __init__(self) -> None:
        """Initialize VictreeBot."""
        # Load environment variables into object
        self.load_environment_variables()

        self.version = "Latest Version"
        self.raids = {}

        logging.getLogger(__name__).debug("Initializing VictreeBot.....")
        super().__init__(token=EnvVarLoader.load_env_variable("BOT_TOKEN"), intents=hikari.Intents.ALL, banner=None)
        logging.getLogger(__name__).info("Initialized VictreeBot!")

    def load_environment_variables(self) -> None:
        """Load environment variables for the bot to use."""
        self.vars = VictreeBotBotVariables()
        self.vars.BOT_NAME = EnvVarLoader.load_env_variable("BOT_NAME")
        self.vars.BOT_PERM = EnvVarLoader.load_env_variable("BOT_PERM")
        self.vars.BOT_INVITE_LINK = EnvVarLoader.load_env_variable("BOT_INVITE_LINK")
        self.vars.SUPPORT_SERVER_LINK = EnvVarLoader.load_env_variable("SUPPORT_SERVER_LINK")
        self.vars.SUPPORT_SERVER_ID = EnvVarLoader.load_env_variable("SUPPORT_SERVER_ID")
        self.vars.SUPPORT_SERVER_BUG_CHANNEL = EnvVarLoader.load_env_variable("SUPPORT_SERVER_BUG_CHANNEL")
        self.vars.SUPPORT_SERVER_FEATURE_IMPROVEMENT_CHANNEL = EnvVarLoader.load_env_variable(
            "SUPPORT_SERVER_FEATURE_IMPROVEMENT_CHANNEL"
        )
        self.vars.SUPPORT_SERVER_FEATURE_REQUEST_CHANNEL = EnvVarLoader.load_env_variable(
            "SUPPORT_SERVER_FEATURE_REQUEST_CHANNEL"
        )
        self.vars.DB_HOST = EnvVarLoader.load_env_variable("DB_HOST")
        self.vars.DB_PORT = int(EnvVarLoader.load_env_variable("DB_PORT"))
        self.vars.DB_DATABASENAME = EnvVarLoader.load_env_variable("DB_DATABASENAME")
        self.vars.API_RELEASE_URL_GITHUB = EnvVarLoader.load_env_variable("API_RELEASE_URL_GITHUB")
        self.vars.ENVIRONMENT = EnvVarLoader.load_env_variable("ENVIRONMENT")
        self.vars.SEQ_ENDPOINT_TRACES = EnvVarLoader.load_optional_env_variable("SEQ_ENDPOINT_TRACES")
        self.vars.SEQ_ENDPOINT_LOGS = EnvVarLoader.load_optional_env_variable("SEQ_ENDPOINT_LOGS")
        self.vars.SERVICE_NAME = EnvVarLoader.load_env_variable("SERVICE_NAME")
        self.vars.LOG_LEVEL = EnvVarLoader.load_env_variable("LOG_LEVEL")

    def initialize_handlers(self) -> None:
        """Initialize different handlers."""
        logging.getLogger(__name__).debug("Initializing ActivityHandler.....")
        self.activity_handler = ActivityHandler(self)
        logging.getLogger(__name__).info("Initialized ActivityHandler!")

        # New
        # Initialize DatabaseHandler
        logging.getLogger(__name__).debug("Initializing DatabaseHandler.....")
        self.database = DatabaseHandler(self)
        logging.getLogger(__name__).info("Initialized DatabaseHandler!")

    def initialize_services(self) -> None:
        """Initialize different services."""
        # Initialize DiscordService
        self._initialize_discord_services()

        # Initialize utils
        logging.getLogger(__name__).debug("Initializing GlobalUtils.....")
        self.utils = GlobalUtils(self)
        logging.getLogger(__name__).info("Initialized GlobalUtils.....")

    def _initialize_discord_services(self) -> None:
        logging.getLogger(__name__).debug("Initializing DiscordService.....")
        self.discord_service = DiscordService(EnvVarLoader.load_env_variable("BOT_TOKEN"))
        logging.getLogger(__name__).info("Initialized DiscordService.....")

        # Initialize DiscordCacheService
        logging.getLogger(__name__).debug("Initializing DiscordCacheService.....")
        self.discord_cache_service = self.cache
        logging.getLogger(__name__).info("Initialized DiscordCacheService.....")

    def check_latest_version(self) -> str:
        """Check the latest version number on the GitHub repository."""
        logging.getLogger(__name__).debug("Checking latest version number.....!")
        version = "Latest Version"
        try:
            headers = {"Authorization": "Bearer " + EnvVarLoader.load_env_variable("API_BEARER_GITHUB")}
            response = requests.get(url=self.vars.API_RELEASE_URL_GITHUB, headers=headers, timeout=10)
            response = response.json()
            version = response["tag_name"]
            logging.getLogger(__name__).info("Found latest version, continuing with: '%s'!", version)
        except Exception:
            logging.getLogger(__name__).exception(
                "Checking latest version number failed, continuing with: 'Latest Version'!"
            )
        self.version = version
        return version

    # RUN
    def create_client(self) -> None:
        """Create the lightbulb client for handling commands."""
        self.client = lightbulb.client_from_app(self)
        # Create registry for dependency injection
        self.di_default_registry = self.client.di.registry_for(lightbulb.di.Contexts.DEFAULT)

    def run(
        self,
        *,
        activity: hikari.Activity | None = None,
        afk: bool = False,
        asyncio_debug: bool | None = None,
        check_for_updates: bool = True,
        close_passed_executor: bool = False,
        close_loop: bool = True,
        coroutine_tracking_depth: int | None = None,
        enable_signal_handlers: bool | None = None,
        idle_since: datetime.datetime | None = None,
        ignore_session_start_limit: bool = False,
        large_threshold: int = 250,
        propagate_interrupts: bool = False,
        status: hikari.Status = presences.Status.ONLINE,
        shard_ids: Sequence[int] | None = None,
        shard_count: int | None = None,
        startup_window_delay: int = 5,
    ) -> None:
        """Start and run."""
        logging.getLogger(__name__).debug("Creating VictreebotBotClient.....")
        self.create_client()
        logging.getLogger(__name__).info("Created VictreebotBotClient!")

        logging.getLogger(__name__).debug("Subscribing to base events.....")
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_stopped)
        logging.getLogger(__name__).info("Subscribed to base events!")

        return super().run(
            activity=activity,
            afk=afk,
            asyncio_debug=asyncio_debug,
            check_for_updates=check_for_updates,
            close_passed_executor=close_passed_executor,
            close_loop=close_loop,
            coroutine_tracking_depth=coroutine_tracking_depth,
            enable_signal_handlers=enable_signal_handlers,
            idle_since=idle_since,
            ignore_session_start_limit=ignore_session_start_limit,
            large_threshold=large_threshold,
            propagate_interrupts=propagate_interrupts,
            status=status,
            shard_ids=shard_ids,
            shard_count=shard_count,
            startup_window_delay=startup_window_delay,
        )

    # EVENTS
    async def on_starting(self, _: hikari.StartingEvent) -> None:
        """Handle the hikari.StartingEvent."""
        logging.getLogger(__name__).info("hikari.StartingEvent fired.....")

        # Check version
        self.check_latest_version()
        # Initialize handlers
        self.initialize_handlers()
        # Initialize services
        self.initialize_services()

        logging.getLogger(__name__).debug("Loading extensions.....")
        await self.client.load_extensions_from_package(extensions, recursive=True)
        await self.client.start()
        logging.getLogger(__name__).info("Loaded extensions!")

        # Open Database connection
        logging.getLogger(__name__).debug("Opening database connection.....")
        await self.database.create_engine()
        logging.getLogger(__name__).info("Opened database connection!")

        # Setup activity handler
        logging.getLogger(__name__).debug("Staring ActivityHandler and task")
        await self.activity_handler.setup_activities()
        self.activity_handler_task = asyncio.create_task(self.activity_handler.change_activity())
        logging.getLogger(__name__).info("Started ActivityHandler and task")

        # Start DiscordService
        logging.getLogger(__name__).debug("Starting DiscordService.....")
        await self.discord_service.start()
        logging.getLogger(__name__).info("Started DiscordService!")

    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        """Handle the hikari.StoppingEvent."""
        logging.getLogger(__name__).info("hikari.StoppingEvent fired.....")

        logging.getLogger(__name__).debug("Stopping ActivityHandler schedule")
        self.activity_handler_task.cancel()
        logging.getLogger(__name__).info("Stopped ActivityHandler schedule")

    async def on_started(self, _: hikari.StartedEvent) -> None:
        """Handle the hikari.StartedEvent."""
        logging.getLogger(__name__).info("hikari.StartedEvent fired.....")

        logging.getLogger(__name__).debug("Registering VictreeBot in DI.....")
        self.di_default_registry.register_factory(Bot, lambda: self)
        logging.getLogger(__name__).info("Registered VictreeBot in DI.....")

    async def on_stopped(self, _: hikari.StoppedEvent) -> None:
        """Handle the hikari.StoppedEvent."""
        logging.getLogger(__name__).info("hikari.StoppedEvent fired.....")
