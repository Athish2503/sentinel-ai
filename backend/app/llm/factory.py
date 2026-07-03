from typing import Optional
from app.llm.base import BaseLLMProvider
from app.llm.groq_provider import GroqProvider


class LLMFactory:
    """
    Factory for creating and managing LLM Provider instances.
    Ensures the application never directly instantiates ChatGroq outside this package.
    """
    _instance: Optional[BaseLLMProvider] = None

    @classmethod
    def create(cls) -> BaseLLMProvider:
        """
        Creates and returns a configured BaseLLMProvider instance.
        Caches the provider instance to avoid redundant initialization.

        Returns:
            The configured BaseLLMProvider instance.
        """
        if cls._instance is None:
            cls._instance = GroqProvider()
        return cls._instance
