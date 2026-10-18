# Copyright (c) 2022-present l3keboy

from collections.abc import Iterator
from typing import TypedDict

class PokemonListEntry(TypedDict):
    name: str
    url: str

class APIResource:
    name: str
    id: int
    height: int
    weight: int
    abilities: list[PokemonAbility]

class PokemonAbility:
    ability: APIResource

class SpriteResource:
    url: str

    def __init__(self, sprite_type: str, sprite_id: str | int, **kwargs: object) -> None: ...

class APIResourceList:
    def __init__(self, endpoint: str, force_lookup: bool = ...) -> None: ...
    def __iter__(self) -> Iterator[PokemonListEntry]: ...
    def __len__(self) -> int: ...

def pokemon(id_or_name: str | int, **kwargs: object) -> APIResource: ...
