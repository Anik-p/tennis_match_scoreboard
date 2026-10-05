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
        """
        INSERT INTO Match
        VALUES (UUID,Player1,Player2,Winner,score)
        """
        self._session.add(match_)

    def get_match_by_uuid(self, uuid: str) -> Match | None:
        """
        SELECT * FROM Match
        WHERE UUID = uuid
        LIMIT 1
        """
        return self._session.execute(select(Match)
                                         .where(Match.UUID == uuid)
                                        ).scalar_one_or_none()

    def get_all(self) -> list[Match]:
        """
            SELECT * FROM Match
        """
        return self._session.execute(select(Match)).scalars().all()


    def get_finished(self,
                     player_name: str | None, page: int,
                     per_page: int) -> tuple[list[Match], int]:
        """
        stmt:

            SELECT * FROM Match 
            JOIN Player as p1 ON Match.Player1 = Player.ID
            JOIN Player as p2 ON Match.Player2 = Player.ID
            WHERE Match.Winner IS NOT None AND
            (p1.Name LIKE %player_name% OR
            p2.Name LIKE %player_name%);

        total:

            SELECT COUNT(*) FROM (stmt)

        rows:

            SELECT * FROM stmt
            ORDER BY Maych.ID desc
            LIMIT per_page OFFSET (page - 1) * per_page 
        """
        
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
        """
        Отправляет изменения в базу данных без их окончательной фиксации, то есть без выполнения коммита.
        Это полезно, когда нужно сгенерировать данные, такие как идентификаторы (например, user.id),
        чтобы использовать их до фактического сохранения данных в базе.
        При этом сама транзакция остаётся открытой, и окончательное сохранение происходит позже, при вызове commit
        """
        self._session.flush()