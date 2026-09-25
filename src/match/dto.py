from dataclasses import dataclass

@dataclass
class MatchDTO:
    """DTO для рендеринга страницы /match-score."""
    uuid: str
    player1: str
    player2: str
    player1_id: int
    player2_id: int
    winner: str | None            # имя победителя (None — матч идёт)
    sets: list[int]               # выигранные сеты, порядок [p1, p2]
    games: list[int]              # геймы текущего сета, порядок [p1, p2]
    points: list[str | int]       # очки текущего гейма, порядок [p1, p2]
    match_status: str             # ongoing | finished
    game_status: str              # game | deuce | tiebreak

@dataclass
class FinishedMatchDTO:
    """Строка таблицы на /matches."""
    player1: str
    player2: str
    winner: str | None

@dataclass
class MatchsViewDTO:
    views: list
    total: int
    page: int

@dataclass
class MatchsRepoDTO:
    matchs: list
    total: int
    page: int

@dataclass
class Score:
    sets: dict[str, int]
    games: dict[str, int]
    points: dict[str, str | int]
    match_status: str
    game_status: str