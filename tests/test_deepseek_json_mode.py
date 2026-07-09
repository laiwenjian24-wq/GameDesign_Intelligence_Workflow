"""Tests for DeepSeek JSON mode and parsing."""

import json
from io import BytesIO

import pytest

from src.llm.client import (
    DeepSeekLLMClient,
    LLMProviderError,
    parse_json_object_from_content,
)


def test_parse_json_content_plain_json():
    payload = parse_json_object_from_content('{"intent": "character_identity"}')

    assert payload == {"intent": "character_identity"}


def test_parse_json_content_fenced_json():
    payload = parse_json_object_from_content(
        '```json\n{"intent": "relationship"}\n```'
    )

    assert payload == {"intent": "relationship"}


def test_parse_json_content_invalid_preview_is_clear():
    with pytest.raises(LLMProviderError) as excinfo:
        parse_json_object_from_content("not json at all")

    message = str(excinfo.value)
    assert "DeepSeek response was not valid JSON" in message
    assert "Sanitized response preview: not json at all" in message


class _FakeHTTPResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_deepseek_chat_payload_includes_response_format(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": '{"ok": true}',
                        }
                    }
                ]
            }
        )

    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr("src.llm.client.request.urlopen", fake_urlopen)

    client = DeepSeekLLMClient()
    content = client.chat(
        [{"role": "user", "content": "Return valid JSON only."}],
        temperature=0.0,
        max_tokens=1234,
        require_json=True,
    )

    assert content == '{"ok": true}'
    assert captured["body"]["response_format"] == {"type": "json_object"}
    assert captured["body"]["temperature"] == 0.0
    assert captured["body"]["max_tokens"] == 1234

