from typing import TYPE_CHECKING
from exceptions.domain_error import MatchNotFoundError, InvalidScoreTransitionError
from dataclasses import dataclass

if TYPE_CHECKING:
    from match_entity import Match
    from player.player_repository import PlayerRepository
    from scoring_service import ScoringService
    from match_repository import MatchRepository

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

class MatchService:
    MATCHES_PER_PAGE = 5
    def __init__( self,
                  score_service: ScoringService,
                  match_repo: MatchRepository,
                  player_repo: PlayerRepository):
        self._score_service = score_service
        self._match_repo = match_repo
        self._player_repo = player_repo

    def new_match(self,
                 name_p1: str,
                 name_p2: str) -> MatchDTO:
        """Игроки ищутся по имени, при отсутствии — создаются."""
        player_1 = self._player_repo.get_by_name_player(name_p1)
        player_2 = self._player_repo.get_by_name_player(name_p2)
        if player_1 is None:
            player_1 = self._player_repo.create_player(name_p1)
        if player_2 is None:
            player_2 = self._player_repo.create_player(name_p2)
        return self._to_dto(self._match_repo.create_new_match(player_1.ID, player_2.ID))

    def get_match(self, uuid: str) -> MatchDTO:
        if not uuid:
            raise MatchNotFoundError() 
        match = self._match_repo.get_match_by_uuid(uuid)
        if match is None:
            raise MatchNotFoundError()
        return self._to_dto(match)
    
    def get_all_match(self) -> list[FinishedMatchDTO]:
        return [self._to_dto(row) for row in self._match_repo.get_all()]

    def get_finished_matches(self, page: int, player_name: str | None) -> tuple[list[FinishedMatchDTO], int, int]:
        """Возвращает (строки таблицы, общее количество, количество страниц)."""
        rows, total = self._match_repo.get_finished(player_name, page, self.MATCHES_PER_PAGE)
        views = [FinishedMatchDTO(player1=row.player1.Name,
                                  player2=row.player2.Name,
                                  winner=row.winner.Name if row.winner else None)
                                  for row in rows]
        pages = max(1, -(-total // self.MATCHES_PER_PAGE)) # Округление в меньшую сторону
        return views, total, pages
    
    def award_point(self, uuid: str, winner_id: str) -> MatchDTO:
        match_entity = self._match_repo.get_match_by_uuid(uuid)
        if not match_entity:
            raise MatchNotFoundError()
        try:
            result = self._score_service.award_point(match_entity, winner_id)
            self._match_repo.save(result)
            return self._to_dto(result)
        except Exception as err:
            raise InvalidScoreTransitionError(str(err))

    def _to_dto(self, match: Match) -> MatchDTO:
        score = match.Score
        ids = [str(match.Player1), str(match.Player2)]
        winner_name = match.winner.Name if match.winner else None
        return MatchDTO(
            uuid=match.UUID,
            player1=match.player1.Name,
            player2=match.player2.Name,
            player1_id=match.Player1,
            player2_id=match.Player2,
            winner=winner_name,
            sets=[score.set_point[i] for i in ids],
            games=[score.game_point[i] for i in ids],
            points=[score.score_players[i] for i in ids],
            match_status=score.match_status,
            game_status=score.game_status
        )