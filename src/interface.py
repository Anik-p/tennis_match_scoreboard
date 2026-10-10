from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.match.repository import MatchRepository
    from src.player.repository import PlayerRepository

class AbstractUnitOfWork(ABC):
    
    player_repo: PlayerRepository
    match_repo: MatchRepository

    @abstractmethod
    def __enter__(self) -> AbstractUnitOfWork:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass