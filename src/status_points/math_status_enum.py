from enum import Enum

class MatchStatus(Enum):
    ONGOING = "ongoing"
    FINISHED = "finished"

class GameStatus(Enum):
    GAME = "game"
    DEUCE = "deuce"
    TIEBREAK = "tiebreak"