"""LLMs for the e-commerce agent."""

from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm():
    """Get a large language model."""
    return ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0,
    )


def get_small_llm():
    """Get a lite large language model."""
    return ChatGoogleGenerativeAI(
        model="gemini-flash-latest-lite",
        temperature=0,
    )
