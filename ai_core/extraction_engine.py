"""LangChain powered process element extraction."""

from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser

from .prompts import EXTRACTION_SYSTEM_PROMPT


def build_extraction_chain(model_name: str = "gpt-3.5-turbo-0125"):
    """Build a simple LangChain LLMChain for process extraction.

    Parameters
    ----------
    model_name:
        Name of the chat model to use. Defaults to ``gpt-3.5-turbo-0125``.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXTRACTION_SYSTEM_PROMPT),
            (
                "human",
                "Extract the process elements from the following text:\n{text}",
            ),
        ]
    )
    llm = ChatOpenAI(model_name=model_name, temperature=0)
    return prompt | llm | StrOutputParser()
