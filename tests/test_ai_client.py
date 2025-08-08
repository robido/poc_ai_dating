import os
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.ai import AIClient


def test_ai_client_dependency_injection():
    """The client should use a supplied OpenAI instance when provided."""

    fake_completion = MagicMock()
    fake_choice = MagicMock()
    fake_choice.message.content = "Hi there"
    fake_completion.choices = [fake_choice]
    fake_openai = MagicMock()
    fake_openai.chat.completions.create.return_value = fake_completion

    with patch("talkmatch.ai.OpenAI") as MockOpenAI:
        client = AIClient(openai_client=fake_openai)
        # Default token limit should allow larger responses.
        assert client.max_tokens == 500
        result = client.get_response([{ "role": "user", "content": "Hello" }])
        MockOpenAI.assert_not_called()

    assert result == "Hi there"
    fake_openai.chat.completions.create.assert_called_once()
