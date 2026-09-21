from status_points.math_status_enum import GameStatus, MathStatus
from match.match_entity import Score
from status_points.point_match import LOVE, FORTY, GAME, AD_IN, AD_OUT, ORDER_POINT_GAME
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from match.match_entity import Match

class ScoringService:
    def award_point(self, match_entity: Match, winner_id: str | int) -> Match:
        """
        Сервис для подсчета геймов, сетов, матчей и обновление статуса матча.

        Структура обаботки:
        1. Обаботка сущности матча и отделяем атрибут сущности матча Score
        2. Обрабатываем атрибут из dataclass Score -> game_status и выполняем обновления счета:

           2.1 -- _mode_game - введет счет для режима геймов,
                                при достижения GAME сбрасывает счет методом _finish_game 
           2.2 -- _mode_deuce - введет счет для режима дюьса,
                                при достижения GAME сбрасывает счет методом _finish_game 
           2.3 -- _mode_tiebreak - введет счет для режима тай-брейка,
                                    при достижения победы в сете обновляет статус матча в атрибуте mathc_status

           _finish_game - |метод, обновляющий счет геймов, сбрасывая очки до LOVE-LOVE ('0':'0'), добавляя счет сетов +1
                          |-> |после проверяет методом _won_set выйгран ли сет
                              |-> |если сет выйгран, сбрасывает счет сетов 0:0 и добавляет счет матча +1
                                  |->|проверяет методом _won_match выйгран ли матч
                                     |->если матч выйгран, обновляет статус матча на MathStatus.FINISHED.value ("finished")

            2.4 -- проверка score.match_status на "finished", если условие выполняется, Match.Winner = winner_id

        3. Проверяем статус игры и обновляем game_status методом _update_game_status (дьюс/тайбрейк),
           если матч завершен(score.match_status == "finished") проверка пропускается
        4. Вывод ответа в виде entity Macth

        Структура ответа:

        Match(UUID=str(uuid.uuid4),
                     Player1="player_1",
                     Player2="player_2",
                     Winner=None,
                     _score=Score)
                     
        Структура Score:

        Score(  set_point = {"Player1_id": 0, "Player2_id": 0},
                game_point = {"Player1_id": 0, "Player2_id": 0}
                score_players = {"Player1_id": "0", "Player2_id": "0"},
                completed_sets = [("3-6")],
                mathc_status = "ongoing",
                game_status = "game")
        """
        winner_id = str(winner_id)
        score: Score = match_entity.Score
        
        if score.match_status == MathStatus.FINISHED.value:
            return match_entity

        if winner_id not in score.score_players:
            raise KeyError(f"winner_id={winner_id} не является участником матча")
        
        game_status: str = score.game_status
        match game_status:
            case GameStatus.GAME.value:
                self._mode_game(winner_id, score)
            case GameStatus.DEUCE.value:
                self._mode_deuce(winner_id, score)
            case GameStatus.TIEBREAK.value:
                self._mode_tiebreak(winner_id, score)

        if score.match_status == MathStatus.FINISHED.value:
            match_entity.Winner = int(winner_id)

        self._update_game_status(score)
        match_entity.Score = score
        return match_entity
    
    def _won_game(self, winner_id: str, score_dict: Score) -> bool:
        score_players: dict = score_dict.score_players
        score_winner = score_players[winner_id]
        return score_winner == GAME

    def _won_set(self, score: Score) -> bool:
        """Сет выигран при 6+ геймах и разнице >= 2, либо на тай-брейке 7-6."""
        pl_set_1, pl_set_2 = sorted(score.game_point.values(), reverse=True)
        return pl_set_1 >= 6 and pl_set_1 - pl_set_2 >= 2 or\
        pl_set_1 == 7 and pl_set_2 == 6

    def _won_match(self, winner_id: str, score: Score) -> bool:
        """Матч играется до двух сетов (best of 3)."""
        return score.set_point[winner_id] >= 2        

    def _update_game_status(self, score: Score) -> None:
        if score.match_status == MathStatus.FINISHED.value:
            return
        pl_score = list(score.score_players.values())
        pl_set = list(score.game_point.values())
        if pl_score == [FORTY, FORTY]:
            score.game_status = GameStatus.DEUCE.value
        elif pl_set == [6, 6] and score.game_status != GameStatus.TIEBREAK.value:
            score.game_status = GameStatus.TIEBREAK.value
            score.score_players = {key: 0 for key in score.score_players}

    def _mode_game(self, winner_id: str, score: Score) -> None:
        next_point = ORDER_POINT_GAME[ORDER_POINT_GAME.index(score.score_players[winner_id]) + 1]
        score.score_players[winner_id] = next_point
        if score.score_players[winner_id] == GAME:
            self._finish_game(winner_id, score)

    def _mode_deuce(self, winner_id: str, score: Score) -> None:
        loser_id = self._to_opponent(winner_id, score)
        loser_score = score.score_players[loser_id]
        winner_score = score.score_players[winner_id]
        if winner_score == AD_IN:
            self._finish_game(winner_id, score)
        elif loser_score == AD_IN:
            score.score_players[winner_id] = FORTY
            score.score_players[loser_id] = FORTY
        else: 
            score.score_players[winner_id] = AD_IN
            score.score_players[loser_id] = AD_OUT

    def _mode_tiebreak(self, winner_id: str, score: Score) -> None:
        """Тай-брейк: очки числовые, победа при 7+ и разнице >= 2."""
        winner_score = score.score_players[winner_id] + 1
        loser_id = self._to_opponent(winner_id, score)
        if winner_score >= 7 and abs(winner_score - score.score_players[loser_id]) >= 2:
            score.score_players[winner_id] = winner_score
            self._finish_game(winner_id, score)
        else:
            score.score_players[winner_id] = winner_score

    def _finish_set(self, score: Score) -> None:
        update_set = {key: 0 for key in score.game_point}
        score.game_point = update_set

    def _finish_game(self, winner_id: str, score: Score) -> None:
        score.score_players = {key: LOVE for key in score.score_players}
        score.game_status = GameStatus.GAME.value
        score.game_point[winner_id] += 1
        if self._won_set(score):
            self._finish_set(score)
            score.set_point[winner_id] += 1 
            if self._won_match(winner_id, score):
                score.match_status = MathStatus.FINISHED.value

    def _to_opponent(self, winner_id: str, score: Score) -> str:
        return next(key for key in score.score_players if key != winner_id)