from typing import TYPE_CHECKING
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from exceptions.app_error import AppErorr
from status_points.math_status_enum import MathStatus
from exceptions.match import MatchNotFoundError, InvalidScoreTransitionError, DatabaseOperationError
from player.entity import Player
from match.mapper import MapperMatch
from match.entity import Match

if TYPE_CHECKING:
    from match.dto import MatchDTO, MatchsViewDTO
    from player.repository import PlayerRepository
    from match.scoring_service.scoring import ScoringService
    from match.repository import MatchRepository

class MatchService:
    MATCHES_PER_PAGE = 5

    def __init__( self,
                  score_service: ScoringService,
                  match_repo: MatchRepository,
                  player_repo: PlayerRepository):

        self._score_service = score_service
        self._match_repo = match_repo
        self._player_repo = player_repo

    def _transations(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            session = self._match_repo._session
            try:
                result = func(self, *args, **kwargs)
                session.commit()
                return result
            except SQLAlchemyError as err:
                session.rollback()
                raise DatabaseOperationError(str(err))
            except AppErorr as err:
                session.rollback()
                raise InvalidScoreTransitionError(str(err))
            except Exception:
                session.rollback()
                raise
        return wrapper

    @_transations
    def new_match(self,
                 name_p1: str,
                 name_p2: str) -> MatchDTO:
        player_1 = self._player_repo.get_by_name(name_p1)
        player_2 = self._player_repo.get_by_name(name_p2)
        if player_1 is None:
            player_1 = Player().create(name_p1)
            self._player_repo.create_player(player_1)
        if player_2 is None:
            player_2 = Player().create(name_p2)
            self._player_repo.create_player(player_2)
        self._match_repo.flush()
        match_ = Match().create(player_1.ID, player_2.ID)
        match_.player1 = player_1
        match_.player2 = player_2
        self._match_repo.add(match_)
        return MapperMatch().to_dto(match_)
    
    @_transations
    def get_match(self, uuid: str) -> MatchDTO:
        if not uuid:
            raise MatchNotFoundError() 
        match_ = self._match_repo.get_match_by_uuid(uuid)
        if match_ is None:
            raise MatchNotFoundError()
        return MapperMatch().to_dto(match_)

    @_transations
    def get_finished_matches(self, page: int, player_name: str | None) -> MatchsViewDTO:
        matchs, total = self._match_repo.get_finished(player_name, page, self.MATCHES_PER_PAGE)
        pages = max(1, -(-total // self.MATCHES_PER_PAGE))
        return MapperMatch().to_view(matchs, total, pages)
    
    @_transations
    def award_point(self, uuid: str, winner_id: str) -> MatchDTO:
        match_ = self._match_repo.get_match_by_uuid(uuid)
        if not match_:
            raise MatchNotFoundError()
        updated_score = self._score_service.award_point(match_.Score, winner_id)
        match_.Score = updated_score
        if match_.Score.match_status == MathStatus.FINISHED.value:
            match_.Winner = winner_id
        self._match_repo.add(match_)
        return MapperMatch().to_dto(match_)
