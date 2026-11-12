"""The chat node: sends the persona plus the conversation to the model."""

from collections.abc import Callable

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

from nova.state import NovaState


def make_chat_node(llm: BaseChatModel, persona: str) -> Callable[[NovaState], dict]:
    """Return a node that replies to the conversation in Nova's voice.

    The persona is prepended as a system message on every call and is never
    written to state, so the saved history stays pure conversation.
    """
    system = SystemMessage(content=persona)

    def chat(state: NovaState) -> dict:
        reply = llm.invoke([system, *state["messages"]])
        return {"messages": [reply]}

    return chat
