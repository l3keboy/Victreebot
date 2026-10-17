from sqlalchemy import Column
from sqlmodel import BigInteger, Field  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import SQLModel
from sqlmodel import UniqueConstraint


class Locations(SQLModel, table=True):
    __tablename__ = "Locations" # type: ignore

    guild_id: int = Field(sa_column=Column(name="guild_id", nullable=False, primary_key=True, type_=BigInteger))
    type: str | None = Field(nullable=True, primary_key=True)
    name: str | None = Field(nullable=True, primary_key=True)
    latitude: float | None = Field(nullable=True)
    longitude: float | None = Field(nullable=True)
    description: str | None = Field(nullable=True, default=None)
    UniqueConstraint("guild_id", "type", "name", name="locations_un")

class LocationsUpdate(SQLModel):
    guild_id: int
    type: str | None = None
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    stats_raids_participated: int | None = None
