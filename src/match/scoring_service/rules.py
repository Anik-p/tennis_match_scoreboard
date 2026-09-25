from status_points.math_status_enum import GameStatus
from status_points.point_match import FORTY, GAME, AD_IN, AD_OUT
from match.scoring_service.dto import DueceDTO

class Rules:

    @staticmethod
    def should_start_tiebreak(games: dict, game_status: str):
        return list(games.values()) == [6,6] and game_status != GameStatus.TIEBREAK.value

    @staticmethod
    def should_enter_deuce(points: dict):
        return list(points.values()) == [FORTY,FORTY]
    
    @staticmethod
    def mode_deuce(winner_score: str, loser_score: str) -> DueceDTO:
        if winner_score == AD_IN:
            return DueceDTO(True)
        elif loser_score == AD_IN:
            return DueceDTO(False, FORTY, FORTY)
        else: 
            return DueceDTO(False, AD_IN, AD_OUT)

    @staticmethod
    def mode_tiebreak(winner_score: int, loser_score: int) -> bool:
        """Тай-брейк: очки числовые, победа при 7+ и разнице >= 2."""
        return winner_score >= 7 and abs(winner_score - loser_score) >= 2

    @staticmethod
    def mode_game(game_status: str) -> bool:
        return game_status == GameStatus.GAME.value
    
    @staticmethod
    def won_game(point: str) -> bool:
        return point == GAME
       
    @staticmethod
    def won_set(sets: dict) -> bool:
        pl_game_1, pl_game_2 = sorted(sets.values(), reverse=True)
        return pl_game_1 >= 6 and pl_game_1 - pl_game_2 >= 2 or\
        pl_game_1 == 7 and pl_game_2 == 6
    
    @staticmethod
    def won_match(sets: dict) -> bool:
        return max(sets.values()) >= 2        