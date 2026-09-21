from enum import Enum

class MathStatus(Enum):
    ONGOING = "ongoing"
    FINISHED = "finished"

class GameStatus(Enum):
    GAME = "game"
    DEUCE = "deuce"
    TIEBREAK = "tiebreak"