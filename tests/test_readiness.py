import logging
import pytest
from talkmatch.readiness import ReadinessEvaluator


class DummyAI:
    def __init__(self, responses):
        self.responses = responses

    def get_response(self, messages):
        return self.responses.pop(0)


def test_is_ready_true(objectives, ready_profile):
    evaluator = ReadinessEvaluator(DummyAI(["80"]))
    assert evaluator.is_ready(objectives, ready_profile)


def test_is_ready_false(objectives, unready_profile):
    evaluator = ReadinessEvaluator(DummyAI(["79"]))
    assert not evaluator.is_ready(objectives, unready_profile)


def test_logs_readiness_result(objectives, ready_profile, caplog):
    evaluator = ReadinessEvaluator(DummyAI(["80"]))
    with caplog.at_level(logging.INFO):
        evaluator.is_ready(objectives, ready_profile)
    assert any("Readiness result" in record.message for record in caplog.records)
