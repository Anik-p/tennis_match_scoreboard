from sqlalchemy import select, func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from match.entity import Match
from player.entity import Player
from exceptions.match import DatabaseOperationError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

class MatchDAO:
    def __init__(self, session: Session):
        self.session = session

    def write_new_match(self, match: Match) -> None:
        try:
            self.session.add(match)
            self.session.commit()
            self.session.refresh(match)
        except SQLAlchemyError as err:
            raise DatabaseOperationError(str(err))

    def get_match_by_uuid(self, uuid: str) -> Match | None:
        try:
            return self.session.execute(select(Match)
                                         .where(Match.UUID == uuid)
                                        ).scalar_one_or_none()
        except SQLAlchemyError as err:
            raise DatabaseOperationError("поиск матча по uuid", err) from err

    def get_all(self):
        try:
            return self.session.execute(select(Match)).scalars().all()
        except SQLAlchemyError as err:
            raise DatabaseOperationError(str(err))

    def save(self, match: Match) -> None:
        try:
            self.session.add(match)
            self.session.commit()
        except SQLAlchemyError as err:
            self.session.rollback()
            raise DatabaseOperationError("сохранение матча", err) from err

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
        try:
            total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
            rows = self.session.scalars(stmt.order_by(Match.ID.desc())
                                        .offset((page - 1) * per_page)
                                        .limit(per_page)).all()
            return list(rows), total
        except SQLAlchemyError as err:
            raise DatabaseOperationError("поиск завершённых матчей", err) from err