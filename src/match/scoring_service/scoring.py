from status_points.math_status_enum import GameStatus, MathStatus
from match.scoring_service.rules import Rules
from status_points.point_match import LOVE, ORDER_POINT_GAME, GAME
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model import Score

class ScoringService:
    def award_point(self, score: Score, winner_id: str | int) -> Score:
        if score.match_status == MathStatus.FINISHED.value:
            return score

        winner_id = str(winner_id)

        if winner_id not in score.points:
            raise KeyError(f"winner_id={winner_id} не является участником матча")

        game_status: str = score.game_status
        match game_status:
            case GameStatus.GAME.value:
                self._game(score, winner_id)
            case GameStatus.DEUCE.value:
                self._duece(score, winner_id)
            case GameStatus.TIEBREAK.value:
                self._tiebreak(score, winner_id)
        return self._update_game_status(score)

    def _game(self, score: Score, winner_id: str):
        self._mode_game(winner_id, score)
        if Rules.won_game(score.points[winner_id]):
            self._finish_game(winner_id, score)

    def _duece(self, score: Score, winner_id: str):
        loser_id = str(self._to_opponent(winner_id, score))
        result = Rules.mode_deuce(score.points[winner_id], score.points[loser_id])
        if result.status:
            self._finish_game(winner_id, score)
        else:
            score.points[winner_id] = result.winner
            score.points[loser_id] = result.loser

    def _tiebreak(self, score: Score, winner_id: str):
        loser_id = str(self._to_opponent(winner_id, score))
        score.points[winner_id] += 1
        if Rules.mode_tiebreak(score.points[winner_id], score.points[loser_id]):
            self._finish_game(winner_id, score)

    def _update_game_status(self, score: Score) -> Score:
        if not score.match_status == MathStatus.FINISHED.value:
            if Rules.should_start_tiebreak(score.games, score.game_status):
                self._start_tiebreak(score)
            elif Rules.should_enter_deuce(score.points):
                score.game_status = GameStatus.DEUCE.value
        return score
    
    def _mode_game(self, winner_id: str, score: Score) -> None:
        if score.points[winner_id] != GAME:
            next_point = ORDER_POINT_GAME[ORDER_POINT_GAME.index(score.points[winner_id]) + 1]
            score.points[winner_id] = next_point

    def _finish_game(self, winner_id: str, score: Score) -> None:
        score.points = {key: LOVE for key in score.points}
        score.game_status = GameStatus.GAME.value
        score.games[winner_id] += 1
        if Rules.won_set(score.games):
            self._update_set(score)
            score.sets[winner_id] += 1 
            if Rules.won_match(score.sets):
                score.match_status = MathStatus.FINISHED.value  

    def _start_tiebreak(self, score: Score) -> None:
        score.points = {key: 0 for key in score.points}
        score.game_status = GameStatus.TIEBREAK.value

    def _update_set(self, score: Score) -> None:
        score.games = {key: 0 for key in score.games}

    def _to_opponent(self, winner_id: str, score: Score) -> str:
        return next(key for key in score.points if key != winner_id)            