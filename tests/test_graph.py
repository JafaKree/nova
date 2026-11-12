from langchain_core.messages import HumanMessage, SystemMessage

from nova.graph import build_graph
from nova.persona import PERSONA_PATH, load_persona


def config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def test_persona_file_ships_with_package():
    assert PERSONA_PATH.exists()
    assert "Nova" in load_persona().prompt


def test_one_turn_appends_user_and_reply(fake_llm):
    graph = build_graph(llm=fake_llm, persona="Be kind.")

    result = graph.invoke({"messages": [HumanMessage("hello")]}, config("t1"))

    assert [m.type for m in result["messages"]] == ["human", "ai"]
    assert result["messages"][-1].content == "Hi Alex!"


def test_history_is_remembered_within_a_thread(fake_llm):
    graph = build_graph(llm=fake_llm, persona="Be kind.")

    graph.invoke({"messages": [HumanMessage("hello")]}, config("t1"))
    result = graph.invoke({"messages": [HumanMessage("again")]}, config("t1"))

    assert [m.content for m in result["messages"]] == ["hello", "Hi Alex!", "again", "Still here."]
    # The second call saw the whole conversation, with the persona first.
    assert [m.content for m in fake_llm.calls[1]] == ["Be kind.", "hello", "Hi Alex!", "again"]


def test_threads_are_separate(fake_llm):
    graph = build_graph(llm=fake_llm, persona="Be kind.")

    graph.invoke({"messages": [HumanMessage("hello")]}, config("t1"))
    result = graph.invoke({"messages": [HumanMessage("new chat")]}, config("t2"))

    assert [m.content for m in result["messages"]] == ["new chat", "Still here."]


def test_persona_is_never_saved_in_state(fake_llm):
    graph = build_graph(llm=fake_llm, persona="Be kind.")

    result = graph.invoke({"messages": [HumanMessage("hello")]}, config("t1"))

    assert not any(isinstance(m, SystemMessage) for m in result["messages"])


def test_default_build_needs_no_running_ollama():
    # Building with the real ChatOllama must not connect until it is invoked.
    graph = build_graph()

    assert "chat" in graph.nodes
