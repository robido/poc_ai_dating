import pytest
from talkmatch.session_manager import SessionManager
import pytest
from talkmatch.session_manager import SessionManager
from talkmatch.personas import Persona
from talkmatch import filters


class DummyAI:
    def __init__(self, responses):
        self.responses = responses

    def get_response(self, messages):
        return self.responses.pop(0) if self.responses else ""


class DummyFactory:
    def __init__(self, responses_per_client):
        self.responses_per_client = responses_per_client

    def __call__(self):
        responses = self.responses_per_client.pop(0)
        return DummyAI(responses)


def test_session_manager_respects_readiness_filter(
    tmp_path, objectives, ready_profile, unready_profile, monkeypatch
):
    personas = [Persona("A", "a"), Persona("B", "b"), Persona("C", "c")]
    factory = DummyFactory([
        ["80", "79", "80"],  # AI for readiness filter
        [],  # AI for session A
        [],  # AI for session B
        [],  # AI for session C
        ["0.9"],  # AI for matcher (A vs C)
    ])
    manager = SessionManager(personas=personas, base_dir=tmp_path, ai_client_factory=factory)

    manager.profile_store.profiles.update({
        "A": ready_profile,
        "B": unready_profile,
        "C": ready_profile,
    })

    monkeypatch.setattr(filters, "PROFILE_OBJECTIVES", objectives)

    manager.calculate()

    assert manager.sessions["A"].matched_persona == "C"
    assert manager.sessions["C"].matched_persona == "A"
    assert manager.sessions["B"].matched_persona is None
