# Copyright (c) 2022-present l3keboy

import datetime
import zoneinfo

from sqlalchemy import Column
from sqlmodel import BigInteger  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import DateTime  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import Field  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import SQLModel


class Guilds(SQLModel, table=True):
    __tablename__ = "Guilds"  # pyright: ignore[reportAssignmentType]

    guild_id: int = Field(sa_column=Column(name="guild_id", nullable=False, primary_key=True, type_=BigInteger))
    guild_owner_id: int = Field(nullable=False, sa_type=BigInteger)
    created_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.datetime.now(zoneinfo.ZoneInfo("UTC")),
    )
