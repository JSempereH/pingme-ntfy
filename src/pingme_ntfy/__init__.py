# SPDX-License-Identifier: EUPL-1.2
"""pingme-ntfy: send a push notification to your phone with a single call.

Usage:
    from pingme_ntfy import ping
    ping("Training finished")

Configuration is read from environment variables:
    NTFY_TOPIC   (required) the ntfy topic to publish to
    NTFY_SERVER  (optional) server URL, defaults to https://ntfy.sh
    NTFY_TOKEN   (optional) access token for protected topics/servers

ping() never raises. On any failure it logs a warning and returns False,
so the calling script keeps running.
"""

import json
import logging
import os
import urllib.request
from importlib import metadata

__all__ = ["ping"]
try:
    __version__ = metadata.version("pingme-ntfy")
except Exception:
    __version__ = "unknown"

DEFAULT_SERVER = "https://ntfy.sh"
TIMEOUT_SECONDS = 10

log = logging.getLogger("pingme_ntfy")


def ping(message, title=None, priority=None, tags=None):
    """Send `message` to the configured ntfy topic.

    Args:
        message: text to send (anything convertible to str).
        title: optional notification title.
        priority: optional int from 1 (min) to 5 (max), default is 3.
        tags: optional list of tags or emoji shortcodes, e.g. ["warning"].

    Returns:
        True if the server accepted the message, False otherwise.
    """
    try:
        topic = os.environ.get("NTFY_TOPIC", "").strip()
        if not topic:
            log.warning("pingme-ntfy: NTFY_TOPIC is not set, message not sent")
            return False

        server = os.environ.get("NTFY_SERVER", "").strip() or DEFAULT_SERVER
        token = os.environ.get("NTFY_TOKEN", "").strip()

        payload = {"topic": topic, "message": str(message)}
        if title:
            payload["title"] = str(title)
        if priority is not None:
            payload["priority"] = int(priority)
        if tags:
            payload["tags"] = [str(t) for t in tags]

        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token

        request = urllib.request.Request(
            server.rstrip("/"),
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return 200 <= response.status < 300

    except Exception as exc:
        log.warning("pingme-ntfy: could not send message: %s", exc)
        return False


def main():
    """Command line entry point: pingme-ntfy "your message"."""
    import sys

    text = " ".join(sys.argv[1:]) or "Hello from pingme-ntfy"
    sys.exit(0 if ping(text) else 1)
