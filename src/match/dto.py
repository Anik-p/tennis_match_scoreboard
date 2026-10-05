from dataclasses import dataclass

@dataclass
class MatchDTO:
    uuid: str
    player1: str
    player2: str
    player1_id: int
    player2_id: int
    winner: str | None            
    sets: list[int]               
    games: list[int]              
    points: list[str | int]       
    match_status: str            
    game_status: str  
                
@dataclass
class FinishedMatchDTO:
    player1: str
    player2: str
    winner: str | None

@dataclass
class MatchesViewDTO:
    matchs: list
    total: int
    page: int