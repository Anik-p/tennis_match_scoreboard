from typing import TYPE_CHECKING
from status_points.match_status_enum import MatchStatus
from exceptions.match import MatchNotFoundError
from player.entity import Player
from match.mapper import MapperMatch
from match.entity import Match

if TYPE_CHECKING:
    from match.dto import MatchDTO, MatchesViewDTO
    from interface import AbstractUnitOfWork
    from scoring_service.scoring import ScoringService

class MatchService:
    MATCHES_PER_PAGE = 5

    def __init__( self,
                  scoring_service: ScoringService):
        self._scoring_service = scoring_service

    def new_match(  self,
                    uow: AbstractUnitOfWork,
                    name_p1: str,
                    name_p2: str) -> MatchDTO:
        player_1 = uow.player_repo.get_by_name(name_p1)
        player_2 = uow.player_repo.get_by_name(name_p2)
        if player_1 is None:
            player_1 = Player().create(name_p1)
            uow.player_repo.create_player(player_1)
        if player_2 is None:
            player_2 = Player().create(name_p2)
            uow.player_repo.create_player(player_2)
        uow.match_repo.flush()
        match_ = Match().create(player_1.ID, player_2.ID)
        match_.player1 = player_1
        match_.player2 = player_2
        uow.match_repo.add(match_)
        return MapperMatch().to_dto(match_)
    
    def get_match(self, uow: AbstractUnitOfWork, uuid: str) -> MatchDTO:
        if not uuid:
            raise MatchNotFoundError() 
        match_ = uow.match_repo.get_match_by_uuid(uuid)
        if match_ is None:
            raise MatchNotFoundError()
        return MapperMatch().to_dto(match_)

    def get_finished_matches( self,
                              uow: AbstractUnitOfWork,
                              page: int,
                              player_name: str | None) -> MatchesViewDTO:
        matchs, total = uow.match_repo.get_finished(player_name, page, self.MATCHES_PER_PAGE)
        pages = max(1, -(-total // self.MATCHES_PER_PAGE))
        return MapperMatch().to_view(matchs, total, pages)
    
    def award_point( self,
                     uow: AbstractUnitOfWork,
                     uuid: str,
                     winner_id: str) -> MatchDTO:
        match_ = uow.match_repo.get_match_by_uuid(uuid)
        if not match_:
            raise MatchNotFoundError()
        updated_score = self._scoring_service.award_point(match_.Score, winner_id)
        match_.Score = updated_score
        if match_.Score.match_status == MatchStatus.FINISHED:
            match_.Winner = winner_id
        uow.match_repo.add(match_)
        return MapperMatch().to_dto(match_)