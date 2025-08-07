import random

from talkmatch.matcher import Matcher


def test_top_matches_deterministic():
    users = ["A", "B", "C"]
    matcher = Matcher(users)
    random.seed(0)
    matcher.calculate()
    top = matcher.top_matches("A", top_n=2)
    assert top[0][0] == "B"
    assert abs(top[0][1] - 0.8444218515250481) < 1e-9
    assert top[1][0] == "C"
    assert abs(top[1][1] - 0.7579544029403025) < 1e-9
