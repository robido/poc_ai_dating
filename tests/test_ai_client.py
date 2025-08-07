import os
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from talkmatch.ai import AIClient


def test_ai_client_returns_text():
    fake_completion = MagicMock()
    fake_choice = MagicMock()
    fake_choice.message.content = "Hi there"
    fake_completion.choices = [fake_choice]

    with patch("talkmatch.ai.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = fake_completion
        client = AIClient(api_key="test-key")
        result = client.get_response([{ "role": "user", "content": "Hello" }])

    assert result == "Hi there"
    instance.chat.completions.create.assert_called_once()
    _, kwargs = instance.chat.completions.create.call_args
    assert kwargs.get("max_tokens") == client.max_tokens
