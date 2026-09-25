"""
Configuration Manager for LM Studio / Bionic Chatbot.

Loads settings securely from environment variables and the local `.env` file.
Ensures no sensitive credentials or internal hostnames are hardcoded in the codebase.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Path to the project root directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
load_dotenv(dotenv_path=BASE_DIR / ".env")


@dataclass
class ChatbotConfig:
    """Application configuration container."""
    base_url: str
    api_key: str
    model: str
    system_prompt: str
    temperature: float
    max_tokens: int


def load_config() -> ChatbotConfig:
    """
    Load configuration from environment with sensible fallbacks.
    Returns:
        ChatbotConfig instance.
    """
    base_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1").strip()
    # Normalize URL: remove trailing slash if present
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    
    # Ensure URL ends with /v1 for OpenAI compatibility
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    api_key = os.getenv("LM_STUDIO_API_KEY", "lm-studio").strip()
    model = os.getenv("LM_STUDIO_MODEL", "default").strip()
    system_prompt = os.getenv(
        "SYSTEM_PROMPT",
        "You are a helpful, thoughtful, and knowledgeable AI assistant running locally."
    ).strip()

    try:
        temperature = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    except ValueError:
        temperature = 0.7

    try:
        max_tokens = int(os.getenv("DEFAULT_MAX_TOKENS", "2048"))
    except ValueError:
        max_tokens = 2048

    return ChatbotConfig(
        base_url=base_url,
        api_key=api_key,
        model=model,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
