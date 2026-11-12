"""Builds Nova's LangGraph: START -> chat -> END."""

from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from nova.llm import make_llm
from nova.nodes.chat import make_chat_node
from nova.settings import load_settings
from nova.state import NovaState

PERSONA_PATH = Path(__file__).with_name("persona.txt")


def load_persona(path: Path = PERSONA_PATH) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_graph(
    llm: BaseChatModel | None = None,
    persona: str | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    """Compile the graph. Every argument has a real default; tests pass fakes.

    History is kept per `thread_id` by the checkpointer (in RAM by default),
    so callers send only the new message each turn.
    """
    llm = llm if llm is not None else make_llm(load_settings())
    persona = persona if persona is not None else load_persona()

    builder = StateGraph(NovaState)
    builder.add_node("chat", make_chat_node(llm, persona))
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)
    return builder.compile(checkpointer=checkpointer or InMemorySaver())
