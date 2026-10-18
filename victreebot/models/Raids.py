# Copyright (c) 2022-present l3keboy

from sqlalchemy import Column
from sqlmodel import BigInteger  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import Field  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import SQLModel
from sqlmodel import UniqueConstraint


class Raids(SQLModel, table=True):
    __tablename__ = "Raids"  # pyright: ignore[reportAssignmentType]

    guild_id: int = Field(sa_column=Column(name="guild_id", nullable=False, primary_key=True, type_=BigInteger))
    raid_id: str = Field(nullable=False, primary_key=True)
    raid_type: str = Field(nullable=False)
    location_type: str = Field(nullable=False)
    location_name: str = Field(nullable=False)
    takes_place_at: str = Field(nullable=False)
    boss: str = Field(nullable=False)
    end_time: float = Field(nullable=True, default=None)
    instinct_present: str | None = Field(nullable=True, default=None)
    mystic_present: str | None = Field(nullable=True, default=None)
    valor_present: str | None = Field(nullable=True, default=None)
    remote_present: str | None = Field(nullable=True, default=None)
    total_attendees: int = Field(nullable=False, default=0)
    raid_message_channel_id: int = Field(nullable=False, sa_type=BigInteger)
    raid_message_id: int = Field(nullable=False, sa_type=BigInteger)
    raid_creator_id: int = Field(nullable=False, sa_type=BigInteger)
    takes_place_at_to_show: str = Field(nullable=True, default=None)
    UniqueConstraint("guild_id", "raid_id", name="raids_un")


class RaidsUpdate(SQLModel):
    guild_id: int
    raid_id: str
    raid_type: str | None = None
    location_type: str | None = None
    location_name: str | None = None
    takes_place_at: str | None = None
    boss: str | None = None
    end_time: float | None = None
    instinct_present: str | None = None
    mystic_present: str | None = None
    valor_present: str | None = None
    remote_present: str | None = None
    total_attendees: int | None = None
    raid_message_channel_id: str | None = None
    raid_message_id: str | None = None
    raid_creator_id: str | None = None
    takes_place_at_to_show: str | None = None
