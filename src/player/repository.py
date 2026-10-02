from sqlalchemy import select
from player.entity import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

class PlayerRepository:
    def __init__(self, session: Session):
        self._session = session

    def create_player(self, player: Player) -> None:
        self._session.add(player)

    def get_by_name(self, name: str) -> Player | None:
        return self._session.execute(select(Player).where(Player.Name == name)).scalar_one_or_none()

    def get_by_id(self, player_id: int) -> Player | None:
        return self._session.get(Player, player_id)