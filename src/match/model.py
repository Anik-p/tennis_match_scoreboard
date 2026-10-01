from dataclasses import dataclass

@dataclass
class Score:
    sets: dict[str, int]
    games: dict[str, int]
    points: dict[str, str | int]
    match_status: str
    game_status: str