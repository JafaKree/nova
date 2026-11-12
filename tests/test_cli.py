import io

from nova.cli import run, stream_reply
from nova.graph import build_graph


def scripted_input(*lines):
    """Fake input(): returns each line in turn, then acts like Ctrl+D."""
    queue = list(lines)

    def fake(prompt: str) -> str:
        if not queue:
            raise EOFError
        return queue.pop(0)

    return fake


def chat(graph, *lines) -> str:
    out = io.StringIO()
    run(graph, input_fn=scripted_input(*lines), out=out, thread_id="test")
    return out.getvalue()


def test_stream_reply_yields_the_reply_text(fake_llm):
    graph = build_graph(llm=fake_llm, persona="Be kind.")

    assert "".join(stream_reply(graph, "hello", "t1")) == "Hi Alex!"


def test_run_prints_replies_and_says_bye(fake_llm):
    output = chat(build_graph(llm=fake_llm, persona="Be kind."), "hello", "/quit")

    assert "Nova: Hi Alex!" in output
    assert output.rstrip().endswith("Bye for now.")


def test_run_keeps_one_conversation(fake_llm):
    chat(build_graph(llm=fake_llm, persona="Be kind."), "hello", "again")

    # The second model call saw the first turn too.
    assert [m.content for m in fake_llm.calls[1]] == ["Be kind.", "hello", "Hi Alex!", "again"]


def test_blank_lines_are_skipped(fake_llm):
    chat(build_graph(llm=fake_llm, persona="Be kind."), "", "   ", "hello")

    assert len(fake_llm.calls) == 1


def test_ctrl_d_exits_cleanly(fake_llm):
    output = chat(build_graph(llm=fake_llm, persona="Be kind."))

    assert "Bye for now." in output
    assert fake_llm.calls == []


def test_ollama_down_shows_a_hint_and_keeps_going(monkeypatch):
    # Point at a port nothing listens on: the real ChatOllama fails to connect.
    monkeypatch.setenv("NOVA_OLLAMA_URL", "http://127.0.0.1:9")

    output = chat(build_graph(persona="Be kind."), "hello", "again", "/quit")

    assert output.count("Can't reach Ollama at http://127.0.0.1:9") == 2
    assert "Bye for now." in output


def test_reply_arrives_in_several_pieces():
    from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
    from langchain_core.messages import AIMessage

    llm = GenericFakeChatModel(messages=iter([AIMessage("one two three")]))
    graph = build_graph(llm=llm, persona="Be kind.")

    pieces = list(stream_reply(graph, "count", "t1"))

    assert len(pieces) > 1
    assert "".join(pieces) == "one two three"
