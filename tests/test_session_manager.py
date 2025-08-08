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


def test_session_manager_handles_matches(tmp_path):
    personas = [Persona("A", "a"), Persona("B", "b")]
    factory = DummyFactory([
        ["profile", "reply"],  # AI for session A
        [],                      # AI for session B
        ["0.8"],                 # AI for matcher
    ])
    manager = SessionManager(personas=personas, base_dir=tmp_path, ai_client_factory=factory)
    captured = {}
    manager.update_callback = lambda m: captured.update({"matches": m})

    manager.calculate()
    assert manager.sessions["A"].matched_persona == "B"
    assert manager.sessions["B"].matched_persona == "A"
    assert captured["matches"]["A"][0][0] == "B"

    manager.sessions["A"].send_client_message("A", "Hi")

    manager.clear()
    assert manager.sessions["A"].matched_persona is None
