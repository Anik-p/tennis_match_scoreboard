from enum import StrEnum

class MatchStatus(StrEnum):
    ONGOING = "ongoing"
    FINISHED = "finished"

class GameStatus(StrEnum):
    GAME = "game"
    DEUCE = "deuce"
    TIEBREAK = "tiebreak"