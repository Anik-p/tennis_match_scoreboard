from db.base import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from dataclasses import asdict
from status_points.point_match import LOVE
from status_points.math_status_enum import MatchStatus, GameStatus
from match.model import Score
import json
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player.entity import Player


class Match(Base):
    """
        Entity матча.
        
        Методы:
            -- create - classmethod метод для создания нового матча
            -- Score - propert/setter, выводит десериализационную строку self._score/ обновляет json представление

        Структура матча:

            Match(UUID=str(uuid.uuid4),
                        Player1=player_1,
                        Player2=player_2,
                        Winner=None,
                        _score=score)

        Структура атрибута _score (десериализационная):

            Score(  sets = {"Player1_id": 0, "Player2_id": 0},
                    games = {"Player1_id": 0, "Player2_id": 0}
                    poits = {"Player1_id": "0", "Player2_id": "0"},
                    match_status = "ongoing",
                    game_status = "game")
    """
    
    __tablename__ = "Matches"
    
    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    UUID: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    Player1: Mapped[int] = mapped_column(Integer, ForeignKey("Players.ID"), nullable=False)
    Player2: Mapped[int] = mapped_column(Integer, ForeignKey("Players.ID"), nullable=False)
    Winner: Mapped[int | None] = mapped_column(Integer, ForeignKey("Players.ID"), nullable=True)
    _score: Mapped[str] = mapped_column(String(200), nullable=False)
    
    player1: Mapped["Player"] = relationship("Player", foreign_keys=[Player1])
    player2: Mapped["Player"] = relationship("Player", foreign_keys=[Player2])
    winner: Mapped["Player | None"] = relationship("Player", foreign_keys=[Winner])
    
    @classmethod
    def create(cls, player_id_1: int, player_id_2: int) -> Match:

        score = Score({player_id_1: 0, player_id_2: 0},
                    {player_id_1: 0, player_id_2: 0},
                    {player_id_1: LOVE, player_id_2: LOVE},
                    MatchStatus.ONGOING.value,
                    GameStatus.GAME.value)
        
        return cls(UUID=str(uuid.uuid4()),
                     Player1=player_id_1,
                     Player2=player_id_2,
                     Winner=None,
                     _score=json.dumps(asdict(score)))

    @property
    def Score(self) -> Score:
        return Score(**json.loads(self._score))

    @Score.setter
    def Score(self, value: Score) -> None:
        self._score = json.dumps(asdict(value))

    def __repr__(self) -> str:
        return f"Math<ID={self.ID}, UUID={self.UUID}, Player1={self.Player1}, Player2={self.Player2}, Winner={self.Winner}, Score={self.Score}>"