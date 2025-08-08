import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.filters import ReadinessFilter
from talkmatch.personas import Persona


class DummyAI:
    def get_response(self, messages):
        return "0"


class DummyProfileStore:
    def read(self, name):
        return ""


def test_readiness_filter_logs_unready_user(capfd):
    rf = ReadinessFilter(DummyAI(), DummyProfileStore())

    class DummyEvaluator:
        def is_ready(self, objectives, profile):
            return False

    rf.evaluator = DummyEvaluator()
    users = ["Dominic"]
    result = rf.filter(users)
    out, _ = capfd.readouterr()
    assert "Dominic has too little profile info" in out
    assert result == []


def test_persona_prompt_mentions_empty_reply():
    p = Persona(name="Test", description="desc")
    prompt = p.system_prompt
    assert "empty message" in prompt

