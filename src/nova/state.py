"""The graph's state: just the conversation so far.

MessagesState gives a `messages` list whose reducer appends new messages
instead of replacing the list. The persona is NOT stored here; the chat node
adds it on every call.
"""

from langgraph.graph import MessagesState


class NovaState(MessagesState):
    pass
