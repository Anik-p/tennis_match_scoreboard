from dataclasses import dataclass
from enum import StrEnum

@dataclass
class Score:
    sets: dict[str, int]
    games: dict[str, int]
    points: dict[str, str | int]
    match_status: StrEnum
    game_status: StrEnum