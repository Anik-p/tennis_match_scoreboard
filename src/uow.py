from sqlalchemy.orm import sessionmaker
from interface import AbstractUnitOfWork
from player.repository import PlayerRepository
from match.repository import MatchRepository
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory
        self.session: Session | None = None 

    def __enter__(self) -> SQLAlchemyUnitOfWork:
        self.session = self._session_factory()
        self.player_repo = PlayerRepository(self.session)
        self.match_repo = MatchRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            self.session.close()
            self.session = None  

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()