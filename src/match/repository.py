from match.dao import MatchDAO
from match.entity import Match
from match.dto import MatchsRepoDTO
from exceptions.match import MatchNotFoundError

class MatchRepository:
    MATCHES_PER_PAGE = 5
    def __init__(self, dao_match: MatchDAO):
        self.dao = dao_match

    def save(self, match: Match) -> None:
        self.dao.save(match)

    def create_new_match(self, player1_id: int, player2_id: int) -> Match:
        match_ = Match().create(player1_id, player2_id)
        self.dao.write_new_match(match_)
        return match_

    def get_all_match(self) -> list[Match]:
        return list(self.dao.get_all())

    def get_match(self, uuid: str) -> Match:
        if not uuid:
            raise MatchNotFoundError() 
        match = self.dao.get_match_by_uuid(uuid)
        if match is None:
            raise MatchNotFoundError()
        return match

    def get_finished_matches(self, page: int, player_name: str | None) -> MatchsRepoDTO:
        """Возвращает (строки таблицы, общее количество, количество страниц)."""
        rows, total = self.dao.get_finished(player_name, page, self.MATCHES_PER_PAGE)
        pages = max(1, -(-total // self.MATCHES_PER_PAGE))
        return MatchsRepoDTO(matchs=rows,
                             total=total,
                             page=pages)