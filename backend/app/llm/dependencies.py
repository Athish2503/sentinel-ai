from app.llm.base import BaseLLMProvider
from app.llm.factory import LLMFactory


def get_llm_provider() -> BaseLLMProvider:
    """
    FastAPI dependency injection helper to retrieve the LLM provider instance.
    Ensures that endpoints can easily acquire a thread-safe BaseLLMProvider.

    Returns:
        The configured BaseLLMProvider.
    """
    return LLMFactory.create()
