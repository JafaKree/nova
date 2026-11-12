from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from nova.nodes.chat import make_chat_node


def test_chat_returns_only_the_new_reply(fake_llm):
    chat = make_chat_node(fake_llm, persona="Be kind.")

    update = chat({"messages": [HumanMessage("hello")]})

    assert len(update["messages"]) == 1
    assert isinstance(update["messages"][0], AIMessage)
    assert update["messages"][0].content == "Hi Alex!"


def test_chat_prepends_persona_then_history(fake_llm):
    chat = make_chat_node(fake_llm, persona="Be kind.")
    history = [HumanMessage("hello"), AIMessage("hi"), HumanMessage("how are you?")]

    chat({"messages": history})

    prompt = fake_llm.calls[0]
    assert prompt[0] == SystemMessage("Be kind.")
    assert prompt[1:] == history
