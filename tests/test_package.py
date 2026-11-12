"""Smoke test: the package installs and its main dependencies import."""


def test_nova_imports():
    import nova

    assert nova.__doc__


def test_dependencies_import():
    import langchain_ollama  # noqa: F401
    import langgraph  # noqa: F401
