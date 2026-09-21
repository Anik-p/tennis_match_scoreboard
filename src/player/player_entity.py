from sqlalchemy import Column, Integer, String
from db.base import Base

class Player(Base):

    __tablename__ = "Players"
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False, unique=True)

    @classmethod
    def create(cls, name: str) -> Player:
        return cls(Name=name)

    def __repr__(self) -> str:
        return f"Player<ID={self.ID}, Name={self.Name}>"