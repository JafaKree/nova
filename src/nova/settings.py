"""Model settings for Nova.

Defaults live here. Any value can be overridden on one machine with an
environment variable, so the PC and the Jetson can differ without code edits:

    NOVA_MODEL       Ollama model name      (default: qwen3.5:9b)
    NOVA_OLLAMA_URL  Ollama server address  (default: http://localhost:11434)
"""

import os
from dataclasses import dataclass

DEFAULT_MODEL = "qwen3.5:9b"
DEFAULT_OLLAMA_URL = "http://localhost:11434"


@dataclass(frozen=True)
class Settings:
    model: str = DEFAULT_MODEL
    ollama_url: str = DEFAULT_OLLAMA_URL


def load_settings() -> Settings:
    """Return the defaults, with any NOVA_* environment variables applied."""
    return Settings(
        model=os.environ.get("NOVA_MODEL", DEFAULT_MODEL),
        ollama_url=os.environ.get("NOVA_OLLAMA_URL", DEFAULT_OLLAMA_URL),
    )
