from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from player.entity import Player
from exceptions.player import DatabaseOperationError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

class PlayerDAO:
    def __init__(self, session: Session):
        self._session = session

    def create_player(self, name: str) -> Player:
        """
            CRATE TABLE Player
            (
                ID INT PRIMARY KEY AUTO_INCRIMENT,
                Name VARCHAR(100) NOT NULL
            );

            INSERT INTO Player(Name)
            VALUES (...);
        """
        try:
            player = Player.create(name)
            self._session.add(player)
            self._session.commit()
            self._session.refresh(player)
            return player
        except SQLAlchemyError as err:
            raise DatabaseOperationError(str(err))

    def get_by_name_player(self, name: str) -> Player | None:
        """
            SELECT * FROM Player
            WHERE Name = name
            LIMIT 1
        """
        try:
            result = self._session.execute(select(Player).where(Player.Name == name)).scalar_one_or_none()
            return result
        except SQLAlchemyError as err:
            raise DatabaseOperationError(str(err))

    def get_by_id_player(self, player_id: int) -> Player | None:
        """
            SELECT * FROM Player
            WHERE ID = player_id
            LIMIT 1
        """
        try:
            result = self._session.execute(select(Player).where(Player.ID == player_id)).scalar_one_or_none()
            return result
        except SQLAlchemyError as err:
            raise DatabaseOperationError(str(err))