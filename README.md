# Nova

Nova is a gentle desktop coworker that chats by text (and later by voice), runs offline with Ollama, and is built on LangGraph.

## Setup

Install [uv](https://docs.astral.sh/uv/), then from this folder:

```sh
uv sync          # installs Python 3.12 and the dependencies into .venv
uv run pytest    # runs the tests
```

## Chat with Nova

Start Ollama and pull the model once (`ollama pull qwen3.5:9b`), then:

```sh
uv run nova
```

Type `/quit` (or press Ctrl+C / Ctrl+D) to leave. Each run starts a fresh conversation.
To use a different model or Ollama server, set `NOVA_MODEL` or `NOVA_OLLAMA_URL`.

## Automatic updates on Linux

Nova can keep itself up to date on a Linux machine with systemd. Once set up, the machine checks GitHub every 5 minutes. When `main` has a new commit, it pulls it, runs `uv sync` and the tests, and restarts Nova. If the tests fail, it rolls back and skips that commit until you push a fix.

One-time setup on that machine:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh   # install uv, then open a new shell
git clone <repo-url> ~/nova
cd ~/nova
bash deploy/linux/install.sh
```

Useful commands:

```sh
systemctl --user start nova-update.service           # update right now
journalctl --user -u nova-update.service -n 50       # see what the updater did
systemctl --user list-timers nova-update.timer       # when the next check runs
systemctl --user disable --now nova-update.timer     # turn automatic updates off
```

Only Nova's code updates automatically. OS updates (`sudo apt upgrade`) are left to you.
