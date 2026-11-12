import pytest

from nova.persona import PersonaFormatError, load_persona, parse_persona

VALID = """+++
schema_version = 1
+++

## Identity
You are Alex's helper.
"""


def test_parse_returns_body_as_prompt():
    assert parse_persona(VALID).prompt == "## Identity\nYou are Alex's helper."


def test_load_reads_a_file(tmp_path):
    path = tmp_path / "persona.md"
    path.write_text(VALID, encoding="utf-8")

    assert load_persona(path).prompt.startswith("## Identity")


def test_body_may_contain_plus_lines_after_settings():
    text = VALID + "\n+++\nstill part of the prompt\n"

    assert "still part of the prompt" in parse_persona(text).prompt


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("You are Jordan's helper.", "must start with"),
        ("+++\nschema_version = 1\n", "no closing"),
        ("+++\nschema_version = \n+++\nHi", "not valid TOML"),
        ("+++\n+++\nHi", "schema_version must be 1"),
        ("+++\nschema_version = 2\n+++\nHi", "schema_version must be 1"),
        ("+++\nschema_version = 1\nvoise = 'x'\n+++\nHi", "unknown settings: voise"),
        ("+++\nschema_version = 1\n+++\n   \n", "no personality text"),
    ],
)
def test_malformed_persona_is_rejected(text, message):
    with pytest.raises(PersonaFormatError, match=message):
        parse_persona(text)
