from __future__ import annotations

import argparse
import json
from urllib import request


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a UTF-8 safe event to the local Discord bridge.")
    parser.add_argument("content", help="Message content to send to Discord")
    parser.add_argument("--username", default="coordinator")
    parser.add_argument("--meeting-id", default="manual-event")
    parser.add_argument("--phase", default="manual")
    parser.add_argument("--trigger-id", default="manual-event")
    parser.add_argument("--thread-id", default="")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()

    payload = {
        "username": args.username,
        "content": args.content,
        "meeting_id": args.meeting_id,
        "phase": args.phase,
        "trigger_id": args.trigger_id,
    }
    if args.thread_id:
        payload["thread_id"] = args.thread_id

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"http://127.0.0.1:{args.port}/event",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with request.urlopen(req, timeout=30) as response:
        print(response.read().decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
