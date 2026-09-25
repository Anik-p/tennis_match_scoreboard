from dataclasses import dataclass

@dataclass
class DueceDTO:
    status: bool
    winner: str | None = None
    loser: str | None = None