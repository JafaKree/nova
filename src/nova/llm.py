"""Builds the chat model Nova talks to."""

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama

from nova.settings import Settings


def make_llm(settings: Settings) -> BaseChatModel:
    """Return a ChatOllama client. No connection is made until it is invoked."""
    return ChatOllama(model=settings.model, base_url=settings.ollama_url)
