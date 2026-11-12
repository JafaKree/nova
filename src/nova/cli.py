"""Text chat with Nova in the terminal. Run with `uv run nova`.

Each run starts a fresh conversation (a new thread_id). Replies stream in
word by word as the model produces them. Type /quit, or press Ctrl+C or
Ctrl+D, to leave.
"""

import sys
import uuid
from collections.abc import Callable, Iterator
from typing import TextIO

import httpx
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from nova.graph import build_graph
from nova.settings import load_settings

QUIT_WORDS = {"/quit", "/exit"}
# ChatOllama surfaces "Ollama is not running" as httpx.ConnectError;
# the ollama library itself may raise the built-in ConnectionError.


def stream_reply(graph: CompiledStateGraph, text: str, thread_id: str) -> Iterator[str]:
    """Send one user message and yield the reply's text pieces as they arrive."""
    config = {"configurable": {"thread_id": thread_id}}
    for chunk, meta in graph.stream(
        {"messages": [HumanMessage(text)]}, config, stream_mode="messages"
    ):
        if meta.get("langgraph_node") == "chat" and chunk.content:
            yield chunk.content


def run(
    graph: CompiledStateGraph,
    input_fn: Callable[[str], str] = input,
    out: TextIO = sys.stdout,
    thread_id: str | None = None,
) -> None:
    """The chat loop. input_fn and out are swappable so tests can drive it."""
    thread_id = thread_id or str(uuid.uuid4())
    print("Nova is here. Type /quit to leave.", file=out)
    while True:
        try:
            text = input_fn("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(file=out)
            break
        if not text:
            continue
        if text.lower() in QUIT_WORDS:
            break

        print("Nova: ", end="", file=out, flush=True)
        try:
            for piece in stream_reply(graph, text, thread_id):
                print(piece, end="", file=out, flush=True)
        except KeyboardInterrupt:
            print(" [stopped]", end="", file=out)
        except (ConnectionError, httpx.ConnectError):
            url = load_settings().ollama_url
            print(f"\n(Can't reach Ollama at {url}. Is it running?)", end="", file=out)
        print(file=out)
    print("Bye for now.", file=out)


def main() -> None:
    run(build_graph())
