from __future__ import annotations
"""Conversation flow management for Casey.

The :class:`ConversationFlowManager` orchestrates follow-up question
generation.  It retrieves relevant memories, generates a next question
with the OpenAI chat model and then rewrites the result to match the
user's tone via :class:`ToneAdapter`.
"""

from typing import List
from .llm_client import chat
from .memory import summarize_context
from .tone_adapter import ToneAdapter
from .vector_memory import VectorMemory

FOLLOWUP_SYSTEM = (
    "You are Casey, an engaging interviewer helping users map their work. "
    "Ask short, relevant follow-up questions."
)


class ConversationFlowManager:
    def __init__(self, memory: VectorMemory | None = None, tone: ToneAdapter | None = None) -> None:
        self.memory = memory or VectorMemory()
        self.tone = tone or ToneAdapter()

    def generate(self, conversation_id: str, history: List[str]) -> str:
        """Return the next follow-up question for ``history``."""
        if not history:
            return "Walk me through the very first step and who does it."

        user_text = history[-1]
        self.tone.update(user_text)
        self.memory.add(conversation_id, user_text)

        prior = summarize_context(history[:-1], max_len=2000)
        related = "\n".join(self.memory.search(user_text))

        messages = [
            {"role": "system", "content": FOLLOWUP_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Conversation so far:\n{prior}\n\n"
                    f"Related notes:\n{related}\n\n"
                    "Ask the next best question in one sentence."
                ),
            },
        ]
        question = chat(messages).strip()
        question = self.tone.apply(question)
        self.memory.add(conversation_id, question)
        return question
