from typing import List
from .llm_client import chat
from .memory import summarize_context, window_messages
from .prompts import INTERVIEWER_SYSTEM, interviewer_user

def next_questions(history: List[str], persona: str = "default") -> List[str]:
    history_plain = summarize_context(history, max_len=2000)
    messages = [
        {"role": "system", "content": INTERVIEWER_SYSTEM},
        {"role": "user",   "content": interviewer_user(history_plain, persona)},
    ]
    messages = window_messages(messages, max_chars=6000)
    try:
        question = chat(messages).strip()
        if not question or len(question) < 3:
            question = "Walk me through the very next step and who does it."
    except Exception:
        question = "Walk me through the very next step and who does it."
    return [question]
