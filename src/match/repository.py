from sqlalchemy import select, func, or_
from sqlalchemy.orm import aliased
from match.entity import Match
from player.entity import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

class MatchRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, match_: Match) -> None:
        self._session.add(match_)

    def get_match_by_uuid(self, uuid: str) -> Match | None:
        return self._session.execute(select(Match)
                                         .where(Match.UUID == uuid)
                                        ).scalar_one_or_none()

    def get_all(self) -> list[Match]:
        return self._session.execute(select(Match)).scalars().all()


    def get_finished(self,
                     player_name: str | None, page: int,
                     per_page: int) -> tuple[list[Match], int]:
        
        p1 = aliased(Player)
        p2 = aliased(Player)
        stmt = (select(Match).join(p1, Match.Player1 == p1.ID)
                             .join(p2, Match.Player2 == p2.ID)
                             .where(Match.Winner.isnot(None)))
        if player_name:
            like = f"%{player_name}%"
            stmt = stmt.where(or_(p1.Name.like(like), p2.Name.like(like)))

        total = self._session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = self._session.scalars(stmt.order_by(Match.ID.desc())
                                        .offset((page - 1) * per_page)
                                        .limit(per_page)).all()
        return list(rows), total

    def flush(self) -> None:
        self._session.flush()