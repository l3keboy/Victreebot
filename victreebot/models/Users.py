# Copyright (c) 2022-present l3keboy

from sqlalchemy import Column
from sqlmodel import BigInteger  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import Field  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import SQLModel
from sqlmodel import UniqueConstraint


class Users(SQLModel, table=True):
    __tablename__ = "Users"  # pyright: ignore[reportAssignmentType]

    guild_id: int = Field(sa_column=Column(name="guild_id", nullable=False, primary_key=True, type_=BigInteger))
    user_id: int = Field(nullable=False, primary_key=True, sa_type=BigInteger)
    friend_codes: str | None = Field(nullable=True, default=None)
    active_locations: str | None = Field(nullable=True, default=None)
    stats_raids_created: int = Field(nullable=False, default=0)
    stats_raids_participated: int = Field(nullable=False, default=0)
    UniqueConstraint("guild_id", "user_id", name="users_un")


class UsersUpdate(SQLModel):
    guild_id: int
    user_id: int
    friend_codes: str | None = None
    active_locations: str | None = None
    stats_raids_created: int | None = None
    stats_raids_participated: int | None = None
