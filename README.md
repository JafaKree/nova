# Nova

Nova is a gentle desktop coworker that chats by text (and later by voice), runs offline with Ollama, and is built on LangGraph.

## Setup

Install [uv](https://docs.astral.sh/uv/), then from this folder:

```sh
uv sync          # installs Python 3.12 and the dependencies into .venv
uv run pytest    # runs the tests
```

## Automatic updates on the Jetson

Once set up, the Jetson checks GitHub every 5 minutes. When `main` has a new commit, it pulls it, runs `uv sync` and the tests, and restarts Nova. If the tests fail, it rolls back and skips that commit until you push a fix.

One-time setup on the Jetson:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh   # install uv, then open a new shell
git clone https://github.com/JafaKree/nova.git ~/nova
cd ~/nova
bash deploy/jetson/install.sh
```

Useful commands:

```sh
systemctl --user start nova-update.service           # update right now
journalctl --user -u nova-update.service -n 50       # see what the updater did
systemctl --user list-timers nova-update.timer       # when the next check runs
systemctl --user disable --now nova-update.timer     # turn automatic updates off
```

Only Nova's code updates automatically. Run OS and JetPack updates (`sudo apt upgrade`) by hand, because they can break CUDA.
