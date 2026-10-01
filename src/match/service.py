from typing import TYPE_CHECKING
from exceptions.app_error import AppErorr
from status_points.math_status_enum import MathStatus
from exceptions.match import MatchNotFoundError, InvalidScoreTransitionError

if TYPE_CHECKING:
    from match.dto import MatchDTO, MatchsViewDTO
    from player.repository import PlayerRepository
    from match.scoring_service.scoring import ScoringService
    from match.repository import MatchRepository

class MatchService:
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
        player_1 = self._player_repo.get_by_name(name_p1)
        player_2 = self._player_repo.get_by_name(name_p2)
        if player_1 is None:
            player_1 = self._player_repo.create_player(name_p1)
        if player_2 is None:
            player_2 = self._player_repo.create_player(name_p2)
        match_ = self._match_repo.create_new_match(player_1.ID, player_2.ID)
        return self._match_repo.to_dto(match_)

    def get_match(self, uuid: str) -> MatchDTO:
        if not uuid:
            raise MatchNotFoundError() 
        match_ = self._match_repo.get_match(uuid)
        if match_ is None:
            raise MatchNotFoundError()
        return self._match_repo.to_dto(match_)

    def get_finished_matches(self, page: int, player_name: str | None) -> MatchsViewDTO:
        return self._match_repo.get_finished_matches(page, player_name)
    
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
            return self._match_repo.to_dto(match_)
        except AppErorr as err:
            raise InvalidScoreTransitionError(str(err))
