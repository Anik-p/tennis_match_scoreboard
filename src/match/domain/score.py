from dataclasses import dataclass
from status_points.match_status_enum import MatchStatus, GameStatus

@dataclass
class Score:
    sets:  dict[str, int] 
    games: dict[str, int] 
    points: dict[str, str | int]
    match_status: MatchStatus
    game_status: GameStatus 