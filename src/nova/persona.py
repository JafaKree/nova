"""Loads Nova's personality file, persona.md.

The file has a small TOML settings block between two `+++` lines, then
the personality itself as Markdown. The Markdown body is the system prompt:

    +++
    schema_version = 1
    +++

    ## Identity
    You are Nova, ...

Only `schema_version` exists for now. Settings such as a greeting, voice or
tools get added here when those features exist. Unknown settings are
rejected so a typo fails loudly instead of being ignored.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

PERSONA_PATH = Path(__file__).with_name("persona.md")
SCHEMA_VERSION = 1
DELIMITER = "+++"
KNOWN_FIELDS = {"schema_version"}


class PersonaFormatError(ValueError):
    """Raised when persona.md is malformed."""


@dataclass(frozen=True)
class Persona:
    prompt: str


def load_persona(path: Path = PERSONA_PATH) -> Persona:
    """Read and validate a persona file."""
    return parse_persona(path.read_text(encoding="utf-8"))


def parse_persona(text: str) -> Persona:
    """Split the settings block from the prompt and validate both."""
    lines = text.strip().splitlines()
    if not lines or lines[0].strip() != DELIMITER:
        raise PersonaFormatError(f"persona must start with a '{DELIMITER}' line")
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == DELIMITER)
    except StopIteration:
        raise PersonaFormatError(f"settings block has no closing '{DELIMITER}' line") from None

    try:
        settings = tomllib.loads("\n".join(lines[1:end]))
    except tomllib.TOMLDecodeError as exc:
        raise PersonaFormatError(f"settings block is not valid TOML: {exc}") from exc

    unknown = settings.keys() - KNOWN_FIELDS
    if unknown:
        raise PersonaFormatError(f"unknown settings: {', '.join(sorted(unknown))}")
    if settings.get("schema_version") != SCHEMA_VERSION:
        raise PersonaFormatError(f"schema_version must be {SCHEMA_VERSION}")

    prompt = "\n".join(lines[end + 1 :]).strip()
    if not prompt:
        raise PersonaFormatError("persona has no personality text after the settings block")
    return Persona(prompt=prompt)
