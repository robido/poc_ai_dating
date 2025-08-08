from talkmatch.session_manager import SessionManager
from talkmatch.personas import Persona


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


def test_linking_progression(tmp_path):
    personas = [Persona("A", "a"), Persona("B", "b")]
    factory = DummyFactory([
        ["p1", "r1", "p2", "r2"],  # session A
        ["p3", "r3", "p4", "r4"],  # session B
        ["0.8"],  # matcher
    ])
    manager = SessionManager(personas=personas, base_dir=tmp_path, ai_client_factory=factory, filters=[], link_threshold=2)
    manager.calculate()
    manager.send_message("A", "hi")
    manager.send_message("B", "hello")
    assert manager.sessions["A"].ambassador.state == "acting"
    manager.send_message("A", "pizza")
    manager.send_message("B", "pizza")
    assert manager.sessions["A"].ambassador.state == "linked"
    assert manager.sessions["B"].ambassador.state == "linked"


def test_official_match_blocks_impersonation(tmp_path):
    personas = [Persona("A", "a"), Persona("B", "b")]
    factory = DummyFactory([
        [],  # session A
        [],  # session B
        ["0.8"],  # matcher first
        [],  # matcher second (skipped due to official match)
    ])
    manager = SessionManager(personas=personas, base_dir=tmp_path, ai_client_factory=factory, filters=[])
    manager.calculate()
    assert manager.sessions["A"].ambassador.persona == "B"
    manager.declare_match("A", "B")
    manager.calculate()
    assert manager.sessions["A"].ambassador.persona is None
    assert manager.sessions["B"].ambassador.persona is None
    assert manager.matcher.matrix["A"]["B"] == 1.0
