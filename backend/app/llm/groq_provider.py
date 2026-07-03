import os
import logging
from typing import Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from app.llm.base import BaseLLMProvider
from app.llm.exceptions import (
    LLMConfigurationError,
    LLMConnectionError,
    LLMAPIError,
)

logger = logging.getLogger("kavalar")


class GroqProvider(BaseLLMProvider):
    """
    Groq LLM provider implementation using ChatGroq.
    Loads API key and model name from the environment, runs with temperature = 0.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("MODEL_NAME")

        if not self.api_key:
            logger.error("GROQ_API_KEY environment variable is not set.")
            raise LLMConfigurationError("GROQ_API_KEY environment variable is not set.")

        if not self.model_name:
            logger.warning("MODEL_NAME environment variable is not set. Defaulting to llama-3-70b-8192.")
            self.model_name = "llama-3-70b-8192"

        try:
            self._client = ChatGroq(
                api_key=self.api_key,
                model=self.model_name,
                temperature=0.0
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatGroq client: {e}", exc_info=True)
            raise LLMConfigurationError(f"Failed to initialize ChatGroq client: {e}") from e

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        """
        Synchronously invoke the Groq LLM with a prompt.
        """
        logger.info(f"Invoking Groq model '{self.model_name}' synchronously.")
        try:
            message = HumanMessage(content=prompt)
            response = self._client.invoke([message], **kwargs)
            return str(response.content)
        except Exception as e:
            err_msg = str(e).lower()
            if any(term in err_msg for term in ("connect", "timeout", "network", "unreachable", "host", "dns")):
                logger.error(f"Groq API connection failure: {e}", exc_info=True)
                raise LLMConnectionError(f"Groq API connection failure: {e}") from e
            
            logger.error(f"Groq API execution failure: {e}", exc_info=True)
            raise LLMAPIError(f"Groq API execution failure: {e}") from e

    async def ainvoke(self, prompt: str, **kwargs: Any) -> str:
        """
        Asynchronously invoke the Groq LLM with a prompt.
        """
        logger.info(f"Invoking Groq model '{self.model_name}' asynchronously.")
        try:
            message = HumanMessage(content=prompt)
            response = await self._client.ainvoke([message], **kwargs)
            return str(response.content)
        except Exception as e:
            err_msg = str(e).lower()
            if any(term in err_msg for term in ("connect", "timeout", "network", "unreachable", "host", "dns")):
                logger.error(f"Groq API async connection failure: {e}", exc_info=True)
                raise LLMConnectionError(f"Groq API async connection failure: {e}") from e
            
            logger.error(f"Groq API async execution failure: {e}", exc_info=True)
            raise LLMAPIError(f"Groq API async execution failure: {e}") from e

    def get_model_name(self) -> str:
        """
        Get the name of the model being used.
        """
        return self.model_name

    def is_available(self) -> bool:
        """
        Performs a lightweight request (max_tokens=1) to verify API connectivity.
        """
        logger.info("Performing availability health check for Groq provider.")
        try:
            # We pass a simple ping and restrict tokens to 1 to minimize latency/cost
            message = HumanMessage(content="ping")
            self._client.invoke([message], max_tokens=1)
            logger.info("Groq provider is active and available.")
            return True
        except Exception as e:
            logger.warning(f"Groq provider is unavailable or returned error: {e}")
            return False
