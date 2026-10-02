from match.dto import MatchDTO, FinishedMatchDTO, MatchsViewDTO
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from match.entity import Match

class MapperMatch:
    @staticmethod
    def to_view(matchs: list[Match], total: int, page: int):
        return MatchsViewDTO(matchs=[FinishedMatchDTO(player1=row.player1.Name,
                                                      player2=row.player2.Name,
                                                      winner=row.winner.Name)
                                    for row in matchs],
                             total=total,
                             page=page)
    
    @staticmethod
    def to_dto(match_: Match) -> MatchDTO:
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