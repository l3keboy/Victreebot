from sqlalchemy import Column
from sqlmodel import BigInteger, Field  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import SQLModel


class Guild_Settings(SQLModel, table=True):
    __tablename__ = "Guild_Settings" # type: ignore

    guild_id: int = Field(sa_column=Column(name="guild_id", nullable=False, primary_key=True, type_=BigInteger))
    language: str = Field(nullable=False)
    gmt: str = Field(nullable=False)
    unit_system: str = Field(nullable=False)
    auto_delete: int | None = Field(nullable=True, default=5)
    raids_channel_id: int | None = Field(nullable=True, default=None, sa_type=BigInteger)
    is_setup: bool = Field(nullable=False, default=False)
    moderator_role_id: int | None = Field(nullable=True, default=None, sa_type=BigInteger)
    instinct_role_id: int | None = Field(nullable=True, default=None, sa_type=BigInteger)
    mystic_role_id: int | None = Field(nullable=True, default=None, sa_type=BigInteger)
    valor_role_id: int | None = Field(nullable=True, default=None, sa_type=BigInteger)
    instinct_emoji_id: int | None = Field(nullable=True, default=None, sa_type=BigInteger)
    mystic_emoji_id: int | None = Field(nullable=True, default=None, sa_type=BigInteger)
    valor_emoji_id: int | None = Field(nullable=True, default=None, sa_type=BigInteger)
    raid_timeout: int = Field(nullable=False, default=900)
    extended_time_format: bool = Field(nullable=False, default=False)

class Guild_SettingsUpdate(SQLModel):
    guild_id: int
    language: str | None = None
    gmt: str | None = None
    unit_system: str | None = None
    auto_delete: int | None = None
    raids_channel_id: int | None = None
    is_setup: bool | None = None
    moderator_role_id: int | None = None
    instinct_role_id: int | None = None
    mystic_role_id: int | None = None
    valor_role_id: int | None = None
    instinct_emoji_id: int | None = None
    mystic_emoji_id: int | None = None
    valor_emoji_id: int | None = None
    raid_timeout: int | None = None
    extended_time_format: bool | None = None
    stats_raids_participated: int | None = None
