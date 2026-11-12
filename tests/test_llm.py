from langchain_ollama import ChatOllama

from nova.llm import make_llm
from nova.settings import Settings


def test_make_llm_uses_settings():
    llm = make_llm(Settings(model="some-model", ollama_url="http://example:1234"))

    assert isinstance(llm, ChatOllama)
    assert llm.model == "some-model"
    assert llm.base_url == "http://example:1234"


def test_thinking_off_by_default():
    assert make_llm(Settings()).reasoning is False


def test_thinking_can_be_turned_on():
    assert make_llm(Settings(think=True)).reasoning is True
