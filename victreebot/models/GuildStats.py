from sqlalchemy import Column
from sqlmodel import BigInteger, Field  # pyright: ignore[reportUnknownVariableType]
from sqlmodel import SQLModel

class Guild_Stats(SQLModel, table=True):
    __tablename__ = "Guild_Stats" # type: ignore

    guild_id: int = Field(sa_column=Column(name="guild_id", nullable=False, primary_key=True, type_=BigInteger))
    raids_completed: int = Field(nullable=False, default=0)
    raids_deleted: int = Field(nullable=False, default=0)
    raids_created: int = Field(nullable=False, default=0)

class Guild_StatsUpdate(SQLModel):
    guild_id: int
    raids_completed: int | None = None
    raids_deleted: int | None = None
    raids_created: int | None = None