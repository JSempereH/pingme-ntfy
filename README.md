# pingme

Send a push notification to your phone from any Python script with one call:

```python
from pingme import ping

ping("Backup finished")
```

It uses [ntfy](https://ntfy.sh), a free and open source notification service. No account, no API key and no dependencies outside the Python standard library.

`ping()` never raises. If something goes wrong (no network, missing configuration, server error), it logs a warning and returns `False`, so your script keeps running.

## Setup from scratch

### 1. Install the ntfy app on your phone

- Android: [Google Play](https://play.google.com/store/apps/details?id=io.heckel.ntfy) or [F-Droid](https://f-droid.org/packages/io.heckel.ntfy/)
- iOS: [App Store](https://apps.apple.com/app/ntfy/id1625396347)

### 2. Pick a topic name

A topic is like a private channel. On the public server anyone who knows the name can read and write to it, so pick something long and random. You can generate one with:

```bash
python3 -c "import secrets; print('pingme-' + secrets.token_urlsafe(16))"
```

The examples below use `my-test-topic-change-me`. Replace it with your own.

### 3. Subscribe to the topic in the app

Open the ntfy app, tap **+**, enter your topic name and subscribe. Leave the server as `ntfy.sh` unless you host your own.

### 4. Set the environment variable on your computer

System wide (all users, all shells, also visible to most services):

```bash
echo 'NTFY_TOPIC=my-test-topic-change-me' | sudo tee -a /etc/environment
```

Or only for your user:

```bash
echo 'export NTFY_TOPIC=my-test-topic-change-me' >> ~/.bashrc
```

Log out and log back in (or open a new terminal for `~/.bashrc`) so the variable is loaded. Check it with:

```bash
echo $NTFY_TOPIC
```

Note: cron jobs do not read `~/.bashrc`. If you call `ping()` from cron, use `/etc/environment` or define the variable at the top of your crontab.

### 5. Install uv

The project is managed with [uv](https://docs.astral.sh/uv/). If you do not have it yet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 6. Get the library

Clone it somewhere on your machine:

```bash
git clone https://github.com/JSempereH/pingme.git ~/pingme
```

Then add it to the uv project where you want to use it:

```bash
cd my-project
uv add --editable ~/pingme
```

`--editable` means changes in `~/pingme` are picked up without reinstalling. Drop it if you prefer a fixed copy. You can also install straight from the repository with `uv add git+https://github.com/JSempereH/pingme`.

To get the `pingme` command available everywhere in your shell:

```bash
uv tool install ~/pingme
```

### 7. Test it

From the `~/pingme` folder:

```bash
uv run pingme "Hello from my computer"
```

Or, if you installed it with `uv tool install`, just `pingme "Hello from my computer"`.

You should get a notification on your phone within a few seconds. The command exits with code `0` on success and `1` on failure, so it also works in shell scripts:

```bash
./backup.sh && pingme "Backup OK" || pingme "Backup FAILED"
```

## Usage

```python
from pingme import ping

ping("Job done")

ping(
    "Disk usage above 90%",
    title="Server alert",
    priority=5,          # 1 (min) to 5 (max), default is 3
    tags=["warning"],    # tags or emoji shortcodes, shown in the app
)

if not ping("Something"):
    print("Notification was not delivered, but the script goes on")
```

A common pattern is to notify when a long task ends, even if it fails:

```python
from pingme import ping

try:
    run_long_task()
    ping("Task finished", tags=["white_check_mark"])
except Exception as e:
    ping(f"Task failed: {e}", priority=5, tags=["x"])
    raise
```

## Configuration

All configuration comes from environment variables:

| Variable      | Required | Default            | Description                                   |
|---------------|----------|--------------------|-----------------------------------------------|
| `NTFY_TOPIC`  | yes      |                    | Topic to publish to                           |
| `NTFY_SERVER` | no       | `https://ntfy.sh`  | Server URL, if you self host ntfy             |
| `NTFY_TOKEN`  | no       |                    | Access token for protected topics or servers  |

## Errors and logging

Failures are reported through the standard `logging` module under the `pingme` logger. By default Python prints them to stderr. To silence them:

```python
import logging
logging.getLogger("pingme").setLevel(logging.ERROR)
```

## Project layout

```
pingme/
├── LICENSE              EUPL-1.2 full text
├── README.md
├── pyproject.toml       package metadata, built with uv_build
└── src/pingme/
    └── __init__.py      all the logic
```

Build a wheel and source distribution with `uv build`.

## License

Licensed under the [European Union Public Licence v. 1.2](https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12) (EUPL-1.2).
