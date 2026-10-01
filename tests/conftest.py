from status_points.point_match import *
from status_points.math_status_enum import *
from match.model import Score
import pytest

PL_1, PL_2 = "PlayreONE", "PlayerTWO"
TEST_UUID = "test_uuid"

@pytest.fixture(scope="function")
def create_score() -> Score:
    return Score({PL_1: 0, PL_2: 0},
                {PL_1: 0, PL_2: 0},
                {PL_1: LOVE, PL_2: LOVE},
                MathStatus.ONGOING.value,
                GameStatus.GAME.value)