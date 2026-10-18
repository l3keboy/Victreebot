class VictreeBotBotVariables:
    """Variables class for the root app containing all required Victreebot variables."""

    BOT_NAME: str
    BOT_PERM: str
    BOT_INVITE_LINK: str
    SUPPORT_SERVER_LINK: str
    SUPPORT_SERVER_ID: str
    SUPPORT_SERVER_BUG_CHANNEL: str
    SUPPORT_SERVER_FEATURE_IMPROVEMENT_CHANNEL: str
    SUPPORT_SERVER_FEATURE_REQUEST_CHANNEL: str
    DB_HOST: str
    DB_PORT: int
    DB_DATABASENAME: str
    API_RELEASE_URL_GITHUB: str
    TEST_BOT_INVITE_LINK: str
    ENVIRONMENT: str = "dev"
    SEQ_ENDPOINT_TRACES: str = ""
    SEQ_ENDPOINT_LOGS: str = ""
    SERVICE_NAME: str = ""
    LOG_LEVEL: str = ""
