#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]{16,}['\"]"),
]


def candidate_path(payload: dict) -> Path | None:
    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    raw = tool_input.get("file_path") or tool_input.get("path")
    if not raw:
        return None
    path = Path(raw).expanduser()
    return path if path.exists() and path.is_file() else None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    path = candidate_path(payload)
    if not path:
        return 0

    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return 0

    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            print(json.dumps({
                "decision": "block",
                "reason": f"Potential secret detected in {path}. Remove it before continuing."
            }))
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
