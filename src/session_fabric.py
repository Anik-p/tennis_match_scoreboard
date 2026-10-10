from uow import SQLAlchemyUnitOfWork
from db.database import SessionLocal

class SessionFabric:
    def __init__(self):
        self._session_local = SessionLocal

    def create_match_service(self) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(self._session_local)