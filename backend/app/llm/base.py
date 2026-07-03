from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """
    Abstract Base Class representing the interface for LLM Providers in Kavalar.
    Ensures decoupled model invocation and standard health check endpoints.
    """

    @abstractmethod
    def invoke(self, prompt: str, **kwargs: Any) -> str:
        """
        Synchronously invoke the LLM with a given prompt and return the string response.

        Args:
            prompt: The input text prompt to send to the LLM.
            **kwargs: Additional parameters for the LangChain runnable or model.

        Returns:
            The text response from the LLM.
        """
        pass

    @abstractmethod
    async def ainvoke(self, prompt: str, **kwargs: Any) -> str:
        """
        Asynchronously invoke the LLM with a given prompt and return the string response.

        Args:
            prompt: The input text prompt to send to the LLM.
            **kwargs: Additional parameters for the LangChain runnable or model.

        Returns:
            The text response from the LLM.
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Retrieve the name of the model currently configured for this provider.

        Returns:
            The string model name.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider API is accessible by making a lightweight request.

        Returns:
            True if available and responsive, False otherwise.
        """
        pass

    @abstractmethod
    def get_client(self) -> Any:
        """
        Retrieve the underlying model client (e.g., ChatGroq instance).
        """
        pass

