from nova.settings import DEFAULT_MODEL, DEFAULT_OLLAMA_URL, load_settings


def test_defaults_without_env(monkeypatch):
    monkeypatch.delenv("NOVA_MODEL", raising=False)
    monkeypatch.delenv("NOVA_OLLAMA_URL", raising=False)

    settings = load_settings()

    assert settings.model == DEFAULT_MODEL == "qwen3.5:9b"
    assert settings.ollama_url == DEFAULT_OLLAMA_URL == "http://localhost:11434"


def test_env_vars_override_defaults(monkeypatch):
    monkeypatch.setenv("NOVA_MODEL", "qwen3.5:2b")
    monkeypatch.setenv("NOVA_OLLAMA_URL", "http://jetson.local:11434")

    settings = load_settings()

    assert settings.model == "qwen3.5:2b"
    assert settings.ollama_url == "http://jetson.local:11434"
