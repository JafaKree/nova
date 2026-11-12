"""Model settings for Nova.

Defaults live here. Any value can be overridden on one machine with an
environment variable, so the PC and the Jetson can differ without code edits:

    NOVA_MODEL       Ollama model name      (default: qwen3.5:9b)
    NOVA_OLLAMA_URL  Ollama server address  (default: http://localhost:11434)
    NOVA_THINK       let the model "think" before answering (default: off)

Thinking is off by default: qwen3.5 otherwise reasons silently for a long
time before the first word appears. Set NOVA_THINK=1 to turn it back on.
"""

import os
from dataclasses import dataclass

DEFAULT_MODEL = "qwen3.5:9b"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_THINK = False
TRUE_WORDS = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    model: str = DEFAULT_MODEL
    ollama_url: str = DEFAULT_OLLAMA_URL
    think: bool = DEFAULT_THINK


def load_settings() -> Settings:
    """Return the defaults, with any NOVA_* environment variables applied."""
    return Settings(
        model=os.environ.get("NOVA_MODEL", DEFAULT_MODEL),
        ollama_url=os.environ.get("NOVA_OLLAMA_URL", DEFAULT_OLLAMA_URL),
        think=_env_flag("NOVA_THINK", DEFAULT_THINK),
    )


def _env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in TRUE_WORDS
