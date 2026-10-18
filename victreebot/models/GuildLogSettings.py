# Copyright (c) 2022-present l3keboy

from sqlalchemy import Column
from sqlmodel import BigInteger  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import Field  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import SQLModel


class Guild_Log_Settings(SQLModel, table=True):
    __tablename__ = "Guild_Log_Settings"  # pyright: ignore[reportAssignmentType]

    guild_id: int = Field(sa_column=Column(name="guild_id", nullable=False, primary_key=True, type_=BigInteger))
    logs_channel_id: int | None = Field(nullable=True, default=None, sa_type=BigInteger)
    log_errors: bool = Field(nullable=False, default=False)
    log_info: bool = Field(nullable=False, default=False)
    log_settings_changed: bool = Field(nullable=False, default=False)
    log_profile_edit: bool = Field(nullable=False, default=False)
    log_profile_view: bool = Field(nullable=False, default=False)
    log_location_add: bool = Field(nullable=False, default=False)
    log_location_delete: bool = Field(nullable=False, default=False)
    log_location_edit: bool = Field(nullable=False, default=False)
    log_location_info: bool = Field(nullable=False, default=False)
    log_location_list: bool = Field(nullable=False, default=False)
    log_raid_create: bool = Field(nullable=False, default=False)
    log_raid_edit: bool = Field(nullable=False, default=False)
    log_raid_delete: bool = Field(nullable=False, default=False)
    log_trade_offer: bool = Field(nullable=False, default=False)
    log_trade_proposal: bool = Field(nullable=False, default=False)
    log_trade_search: bool = Field(nullable=False, default=False)


class Guild_Log_SettingsUpdate(SQLModel):
    guild_id: int
    logs_channel_id: int | None = None
    log_errors: bool | None = None
    log_info: bool | None = None
    log_settings_changed: bool | None = None
    log_profile_edit: bool | None = None
    log_profile_view: bool | None = None
    log_location_add: bool | None = None
    log_location_delete: bool | None = None
    log_location_edit: bool | None = None
    log_location_info: bool | None = None
    log_location_list: bool | None = None
    log_raid_create: bool | None = None
    log_raid_edit: bool | None = None
    log_raid_delete: bool | None = None
    log_trade_offer: bool | None = None
    log_trade_proposal: bool | None = None
    log_trade_search: bool | None = None
