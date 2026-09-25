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
        """
        CRATE TABLE Match
        (
            ID INT PRIMARY KEY AUTO_INCRIMENT,
            UUID VARCHAR(100) NOT NULL,
            Player1 INT, FOREIGN KEY (Player1) REFERENCES Players ("ID") NOT NULL,
            Player2 INT, FOREIGN KEY (Player2) REFERENCES Players ("ID") NOT NULL,
            Winner INT NOT NULL,
            _score VARCHAR(200) NOT NULL
        );

        INSERT INTO Match(UUID, Player1, Player2, Winner, _score)
        VALUES (... ,  ...);
        """
        try:
            self.session.add(match)
            self.session.commit()
            self.session.refresh(match)
        except SQLAlchemyError as err:
            raise DatabaseOperationError(str(err))

    def get_match_by_uuid(self, uuid: str) -> Match | None:
        """
            SELECT * FROM 
            FROM Matrch
            WHERE UUID = uuid
            LIMIT 1
        """
        try:
            return self.session.execute(select(Match)
                                         .where(Match.UUID == uuid)
                                        ).scalar_one_or_none()
        except SQLAlchemyError as err:
            raise DatabaseOperationError("поиск матча по uuid", err) from err

    def get_all(self):
        """
            SELECT * FROM Matrch    
        """
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
        """
        Завершённые матчи (Winner IS NOT NULL) с фильтром по имени игрока и пагинацией.

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
        try:
            total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
            rows = self.session.scalars(stmt.order_by(Match.ID.desc())
                                        .offset((page - 1) * per_page)
                                        .limit(per_page)).all()
            return list(rows), total
        except SQLAlchemyError as err:
            raise DatabaseOperationError("поиск завершённых матчей", err) from err