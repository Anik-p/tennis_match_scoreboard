from typing import TYPE_CHECKING
from exceptions.app_error import AppErorr
from status_points.math_status_enum import MathStatus
from exceptions.match import MatchNotFoundError, InvalidScoreTransitionError
from match.dto import MatchDTO, FinishedMatchDTO, MatchsViewDTO

if TYPE_CHECKING:
    from match.entity import Match
    from player.dao import PlayerDAO
    from match.scoring_service.scoring import ScoringService
    from match.repository import MatchRepository

class MatchService:
    def __init__( self,
                  score_service: ScoringService,
                  match_repo: MatchRepository,
                  player_dao: PlayerDAO):
        self._score_service = score_service
        self._match_repo = match_repo
        self._player_repo = player_dao

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
        match_ = self._match_repo.create_new_match(player_1.ID, player_2.ID)
        return self._to_dto(match_)

    def get_match(self, uuid: str) -> MatchDTO:
        if not uuid:
            raise MatchNotFoundError() 
        match_ = self._match_repo.get_match(uuid)
        if match_ is None:
            raise MatchNotFoundError()
        return self._to_dto(match_)
    
    def get_all_match(self) -> list[FinishedMatchDTO]:
        return [self._to_dto(row) for row in self._match_repo.get_all_match()]

    def get_finished_matches(self, page: int, player_name: str | None) -> MatchsViewDTO:
        matchs_dto = self._match_repo.get_finished_matches(page, player_name)
        view = self._to_views(matchs_dto.matchs)
        return MatchsViewDTO(views=view, total=matchs_dto.total, page=matchs_dto.page)
    
    def award_point(self, uuid: str, winner_id: str) -> MatchDTO:
        match_ = self._match_repo.get_match(uuid)
        if not match_:
            raise MatchNotFoundError()
        try:
            updated_score = self._score_service.award_point(match_.Score, winner_id)
            match_.Score = updated_score
            if match_.Score.match_status == MathStatus.FINISHED.value:
                match_.Winner = winner_id
            self._match_repo.save(match_)
            return self._to_dto(match_)
        except AppErorr as err:
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
            sets=[score.sets[i] for i in ids],
            games=[score.games[i] for i in ids],
            points=[score.points[i] for i in ids],
            match_status=score.match_status,
            game_status=score.game_status
        )

    def _to_views(self, matchs: list[Match]) -> list[FinishedMatchDTO]:
        return [FinishedMatchDTO(player1=row.player1.Name,
                                  player2=row.player2.Name,
                                  winner=row.winner.Name if row.winner else None)
                                  for row in matchs]