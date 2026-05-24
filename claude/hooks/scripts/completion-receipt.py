#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path


REQUIRED_MARKERS = ("Checks run", "Verification", "Checks skipped", "React Doctor")


def main() -> int:
    if os.environ.get("CLAUDE_ALLOW_MISSING_RECEIPT") == "1":
        return 0

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    transcript = payload.get("transcript_path") or payload.get("transcriptPath")
    if not transcript:
        return 0

    path = Path(transcript)
    if not path.exists():
        return 0

    tail = "\n".join(path.read_text(errors="ignore").splitlines()[-80:])
    if any(marker in tail for marker in REQUIRED_MARKERS):
        return 0

    print(json.dumps({
        "decision": "block",
        "reason": "Before stopping, include a completion receipt with what changed, checks run, checks skipped with reasons, and remaining risks."
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
