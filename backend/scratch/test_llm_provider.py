import os
import asyncio
import logging
from dotenv import load_dotenv

# Ensure we load environment variables
load_dotenv()

from app.llm import (
    LLMFactory,
    BaseLLMProvider,
    LLMConfigurationError,
    LLMAPIError,
    LLMConnectionError,
)

# Setup logging to console to see our execution logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_llm_provider")


async def run_tests():
    logger.info("================ STARTING LLM PROVIDER TESTS ================")

    # 1. Test Factory Creation
    logger.info("\n--- 1. Testing LLMFactory.create() ---")
    try:
        provider = LLMFactory.create()
        logger.info(f"Successfully created provider instance of type: {type(provider)}")
        logger.info(f"Model configured: {provider.get_model_name()}")
        assert isinstance(provider, BaseLLMProvider)
    except Exception as e:
        logger.error(f"Failed to create LLM provider: {e}", exc_info=True)
        return

    # 2. Test Availability Check
    logger.info("\n--- 2. Testing provider.is_available() ---")
    try:
        available = provider.is_available()
        logger.info(f"Provider availability status: {available}")
    except Exception as e:
        logger.error(f"Error during is_available check: {e}", exc_info=True)

    # 3. Test Sync Invoke
    logger.info("\n--- 3. Testing synchronous invoke() ---")
    try:
        response = provider.invoke("Return the word 'HELLO' and nothing else.")
        logger.info(f"Synchronous Response: '{response}'")
    except Exception as e:
        logger.error(f"Error during synchronous invoke: {e}", exc_info=True)

    # 4. Test Async Invoke
    logger.info("\n--- 4. Testing asynchronous ainvoke() ---")
    try:
        response = await provider.ainvoke("Return the word 'WORLD' and nothing else.")
        logger.info(f"Asynchronous Response: '{response}'")
    except Exception as e:
        logger.error(f"Error during asynchronous ainvoke: {e}", exc_info=True)

    # 5. Test Error Handling (Invalid/Missing API Key)
    logger.info("\n--- 5. Testing Configuration Exception Handling ---")
    # Temporarily remove API key from env to test config error
    original_key = os.environ.get("GROQ_API_KEY")
    try:
        if original_key:
            del os.environ["GROQ_API_KEY"]
        
        logger.info("Attempting to create provider with missing API key...")
        # Force new instance creation in factory since it is cached
        # We can bypass factory caching or test the class instantiation directly
        from app.llm.groq_provider import GroqProvider
        try:
            GroqProvider()
            logger.error("Expected LLMConfigurationError but none was raised.")
        except LLMConfigurationError as e:
            logger.info(f"Successfully caught expected LLMConfigurationError: {e}")
    finally:
        # Restore API key
        if original_key:
            os.environ["GROQ_API_KEY"] = original_key

    # 6. Test API Exception Handling (Invalid API Key call)
    logger.info("\n--- 6. Testing API Exception Handling ---")
    try:
        os.environ["GROQ_API_KEY"] = "gsk_invalid_key_for_testing_error_handling"
        from app.llm.groq_provider import GroqProvider
        bad_provider = GroqProvider()
        logger.info("Attempting to invoke provider with invalid API key...")
        try:
            bad_provider.invoke("Test prompt")
            logger.error("Expected LLMAPIError but none was raised.")
        except LLMAPIError as e:
            logger.info(f"Successfully caught expected LLMAPIError: {e}")
    finally:
        # Restore original API key
        if original_key:
            os.environ["GROQ_API_KEY"] = original_key

    logger.info("\n================ TESTS COMPLETE ================")


if __name__ == "__main__":
    asyncio.run(run_tests())
