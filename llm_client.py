"""
LLM Client Interface for LM Studio / Bionic.

LM Studio exposes an OpenAI-compatible REST API (typically at http://localhost:1234/v1
or your custom host like http://bionic:1234/v1). This module wraps the official
openai Python SDK to provide:
1. Connection health checks & model discovery.
2. Streaming token generation for interactive chat responses.
3. Informative error messages for local inference issues.
"""

from typing import Generator, List, Dict, Tuple, Optional
from openai import OpenAI, APIConnectionError, APIStatusError


def create_llm_client(base_url: str, api_key: str = "lm-studio", timeout: float = 30.0) -> OpenAI:
    """
    Initialize an OpenAI client pointing to the local LM Studio instance.

    Args:
        base_url: The local endpoint (e.g. 'http://localhost:1234/v1' or 'http://bionic:1234/v1')
        api_key: LM Studio doesn't enforce API keys, but the SDK requires a string.
        timeout: Request timeout in seconds.

    Returns:
        OpenAI client configured for the local endpoint.
    """
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=timeout,
    )


def test_connection(client: OpenAI) -> Tuple[bool, str, List[str]]:
    """
    Test connectivity to LM Studio by querying the models endpoint (/v1/models).

    Returns:
        Tuple of (is_connected: bool, message: str, models: list[str])
    """
    try:
        response = client.models.list()
        models = [m.id for m in response.data] if response.data else []
        return True, "Successfully connected to local LLM server!", models
    except APIConnectionError as e:
        return (
            False,
            f"Could not connect to {client.base_url}. Make sure LM Studio's Local Server is started and reachable.",
            [],
        )
    except APIStatusError as e:
        return False, f"Server responded with error status {e.status_code}: {e.message}", []
    except Exception as e:
        return False, f"Connection failed: {str(e)}", []


def stream_chat_response(
    client: OpenAI,
    messages: List[Dict[str, str]],
    model: str = "default",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> Generator[str, None, None]:
    """
    Send messages to LM Studio and stream the response tokens back in real-time.
    Supports both standard LLMs and reasoning models (with reasoning_content).

    Args:
        client: The OpenAI client pointing to LM Studio.
        messages: Conversation history formatted as [{"role": "user"|"assistant"|"system", "content": "..."}].
        model: Model identifier.
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
        max_tokens: Maximum tokens in the generated response.

    Yields:
        Text chunks as they arrive from the local LLM.
    """
    try:
        response_stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        in_thought = False
        for chunk in response_stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 1. Handle reasoning/thinking models (e.g. Qwen 3, DeepSeek R1)
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                if not in_thought:
                    yield "> **Thinking Process:**\n> "
                    in_thought = True
                # Format thoughts as blockquotes
                formatted_reasoning = reasoning.replace("\n", "\n> ")
                yield formatted_reasoning

            # 2. Handle actual response content
            content = getattr(delta, "content", None)
            if content:
                if in_thought:
                    yield "\n\n---\n\n"
                    in_thought = False
                yield content

    except APIConnectionError:
        yield "\n\n❌ **Error**: Connection to the local LLM server was lost. Please verify LM Studio is running."
    except Exception as e:
        yield f"\n\n❌ **Error during generation**: {str(e)}"
