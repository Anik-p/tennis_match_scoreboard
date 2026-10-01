from match.dao import MatchDAO
from match.entity import Match
from match.dto import MatchDTO, MatchsViewDTO, FinishedMatchDTO
from exceptions.match import MatchNotFoundError

class MatchRepository:
    MATCHES_PER_PAGE = 5
    def __init__(self, dao_match: MatchDAO):
        self.dao = dao_match

    def save(self, match_: Match) -> None:
        self.dao.save(match_)

    def create_new_match(self, player1_id: int, player2_id: int) -> Match:
        match_ = Match().create(player1_id, player2_id)
        self.dao.write_new_match(match_)
        return match_

    def get_match(self, uuid: str) -> Match:
        if not uuid:
            raise MatchNotFoundError() 
        match_ = self.dao.get_match_by_uuid(uuid)
        if match_ is None:
            raise MatchNotFoundError()
        return match_

    def get_finished_matches(self, page: int, player_name: str | None) -> MatchsViewDTO:
        matchs, total = self.dao.get_finished(player_name, page, self.MATCHES_PER_PAGE)
        pages = max(1, -(-total // self.MATCHES_PER_PAGE))
        return self._to_view(matchs, total, pages)

    def _to_view(self, matchs: list[Match], total: int, page: int):
        return MatchsViewDTO(matchs=[FinishedMatchDTO(player1=row.player1.Name,
                                                      player2=row.player2.Name,
                                                      winner=row.winner.Name)
                                    for row in matchs],
                             total=total,
                             page=page)
    
    def to_dto(self, match_: Match) -> MatchDTO:
        score = match_.Score
        ids = [str(match_.Player1), str(match_.Player2)]
        winner_name = match_.winner.Name if match_.winner else None
        return MatchDTO(
            uuid=match_.UUID,
            player1=match_.player1.Name,
            player2=match_.player2.Name,
            player1_id=match_.Player1,
            player2_id=match_.Player2,
            winner=winner_name,
            sets=[score.sets[i] for i in ids],
            games=[score.games[i] for i in ids],
            points=[score.points[i] for i in ids],
            match_status=score.match_status,
            game_status=score.game_status
        )