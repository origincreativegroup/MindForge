from __future__ import annotations
from typing import List
from .conversation_flow import ConversationFlowManager

_manager = ConversationFlowManager()


def next_questions(history: List[str], conversation_id: str = "default") -> List[str]:
    """Return the next question Casey should ask.

    Parameters
    ----------
    history:
        Full conversation transcript with the most recent user message
        placed at the end of the list.
    conversation_id:
        Identifier used for vector-memory storage.
    """
    question = _manager.generate(conversation_id, history)
    return [question]
