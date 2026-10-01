from tests.conftest import PL_1, PL_2
from status_points.point_match import *
from status_points.math_status_enum import *
from match.scoring_service.scoring import ScoringService
import pytest

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from match.entity import Match
    from match.model import Score

@pytest.mark.parametrize("start_score,winner_id,expected", [
                            ((LOVE, LOVE), PL_1, (FIFTEEN, LOVE)),
                            ((FIFTEEN, LOVE), PL_1, (THIRTY, LOVE)),
                            ((THIRTY, LOVE), PL_1, (FORTY, LOVE)),
                            ((FORTY, LOVE), PL_1, (LOVE, LOVE))])

def test_scoring(start_score: str,
                 winner_id: int,
                 expected: str,
                 create_score: Score):
    score = prepare_point(create_score, start_score)
    score_service = ScoringService()
    score_result = score_service.award_point(score, winner_id)
    point_p1, point_p2 = score_result.points.values()
    ex_point_pl1 , ex_point_pl2 = expected
    assert point_p1 == ex_point_pl1 and point_p2 == ex_point_pl2


@pytest.mark.parametrize("winner_id,winner_id_point,expected,mode", [
                            (PL_1, None, (AD_IN, AD_OUT), GameStatus.DEUCE.value),
                            (PL_2, None, (AD_OUT, AD_IN), GameStatus.DEUCE.value),
                            (PL_2, PL_1, (FORTY, FORTY), GameStatus.DEUCE.value),
                            (PL_1, PL_1, (LOVE, LOVE), GameStatus.GAME.value)])
def test_deuce_mod(winner_id: int,
                   winner_id_point: int | None,
                   expected: str,
                   mode: str,
                   create_score: Score):
    score = prepare_deuce(create_score, winner_id_point)
    score_service = ScoringService()
    score_result = score_service.award_point(score, winner_id)
    point_p1, point_p2 = score_result.points.values()
    ex_point_pl1 , ex_point_pl2 = expected
    assert (point_p1 == ex_point_pl1 and point_p2 == ex_point_pl2) and score_result.game_status == mode

@pytest.mark.parametrize("start_score,winner_id,expected,mode", [
                            ((0,0),PL_1, (1,0), GameStatus.TIEBREAK.value),
                            ((0,0),PL_2, (0,1), GameStatus.TIEBREAK.value),
                            ((6,6),PL_2, (6,7), GameStatus.TIEBREAK.value),
                            ((4,5),PL_1, (5,5), GameStatus.TIEBREAK.value),
                            ((4,5),PL_1, (5,5), GameStatus.TIEBREAK.value),
                            ((4,5),PL_1, (5,5), GameStatus.TIEBREAK.value),
                            ((6,6),PL_1, (7,6), GameStatus.TIEBREAK.value),
                            ((6,5),PL_1, (LOVE,LOVE), GameStatus.GAME.value),
                            ((8,8),PL_1, (9,8), GameStatus.TIEBREAK.value),
                            ((10,11),PL_2, (LOVE,LOVE), GameStatus.GAME.value)])
def test_tiebreak_mod(start_score: tuple[int],
                      winner_id: int,
                      expected: tuple[int],
                      mode: str,
                      create_score: Score):
    score = prepare_tiebreak(create_score, start_score)
    score_service = ScoringService()
    score_result = score_service.award_point(score, winner_id)
    point_p1, point_p2 = score_result.points.values()
    ex_point_pl1 , ex_point_pl2 = expected
    assert (point_p1 == ex_point_pl1 and point_p2 == ex_point_pl2) and score_result.game_status == mode
    
@pytest.mark.parametrize("sets,winner_id,expected,mode_match", [
                            ((0,0),PL_1, (1,0), MathStatus.ONGOING.value),
                            ((0,1),PL_1, (1,1), MathStatus.ONGOING.value),
                            ((1,1),PL_1, (2,1), MathStatus.FINISHED.value)])
def test_match_point(sets: tuple[int],
                     winner_id: int,
                     expected: tuple[int],
                     mode_match: str,
                     create_score: Score):
    score = prepare_match_point(create_score, sets)
    score_service = ScoringService()
    score_result = score_service.award_point(score, winner_id)
    set_p1, set_p2 = score_result.sets.values()
    ex_point_pl1 , ex_point_pl2 = expected
    assert (set_p1 == ex_point_pl1 and set_p2 == ex_point_pl2) and score_result.match_status == mode_match

def prepare_match_point(score: Score, set: tuple[int, int]) -> Match:
    set_pl1 , set_pl2 = set
    score.sets[PL_1] = set_pl1
    score.sets[PL_2] = set_pl2
    score.games[PL_1] = 5
    score.games[PL_2] = 4
    score.points[PL_1] = GAME
    score.points[PL_2] = THIRTY
    return score

def prepare_point(score: Score, points_players: tuple[str]) -> Match:
    point_p1, point_p2 = points_players
    score.points[PL_1] = point_p1
    score.points[PL_2] = point_p2
    return score

def prepare_tiebreak(score: Score, game: tuple[int, int]) -> Match:
    score.games = {pl: 6 for pl in score.games}
    score.game_status = GameStatus.TIEBREAK.value
    point_pl1, point_pl2 = game
    score.points[PL_1] = point_pl1
    score.points[PL_2] = point_pl2
    return score

def prepare_deuce(score: Score, winner_id: str | None) -> Match:
    if winner_id is None:
        score.points = {pl: FORTY for pl in  score.points}
    else:
        loser_id = next(key for key in score.points if key != winner_id)
        score.points[winner_id] = AD_IN
        score.points[loser_id] = AD_OUT
    score.game_status = GameStatus.DEUCE.value
    return score