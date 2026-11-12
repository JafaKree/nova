"""Shared test fakes. Nothing here talks to Ollama."""

from typing import Any

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class RecordingChatModel(BaseChatModel):
    """Fake chat model: replies from a script and records every prompt it got."""

    replies: list[str]
    calls: list[list[BaseMessage]] = []

    @property
    def _llm_type(self) -> str:
        return "recording-fake"

    def _generate(self, messages: list[BaseMessage], stop: Any = None, run_manager: Any = None, **kwargs: Any) -> ChatResult:
        self.calls.append(list(messages))
        text = self.replies[(len(self.calls) - 1) % len(self.replies)]
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])


@pytest.fixture
def fake_llm() -> RecordingChatModel:
    return RecordingChatModel(replies=["Hi Alex!", "Still here."], calls=[])
