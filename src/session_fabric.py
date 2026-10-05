from match.repository import MatchRepository
from player.repository import PlayerRepository
from match.scoring_service.scoring import ScoringService
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from exceptions.match import DatabaseOperationError
from typing import Generator
from match.service import MatchService
from db.database import SessionLocal

class SessionFabric:
    def __init__(self):
        self._session_local = SessionLocal
    
    @contextmanager
    def _create_match_service(self) -> Generator[MatchService]:
        session = self._session_local()
        try:
            player_repo = PlayerRepository(session)
            match_repo = MatchRepository(session)
            match_service = MatchService(score_service=ScoringService(),
                                         match_repo=match_repo,
                                         player_repo=player_repo)
            yield match_service
            session.commit()
        except SQLAlchemyError as err:
            session.rollback()
            raise DatabaseOperationError(str(err))
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()