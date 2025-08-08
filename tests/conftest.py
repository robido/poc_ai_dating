import pytest


@pytest.fixture
def objectives():
    return ["hiking"]


@pytest.fixture
def ready_profile():
    return "loves hiking"


@pytest.fixture
def unready_profile():
    return "likes movies"
