#!/usr/bin/env python3
import json
import re
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    command = (
        payload.get("tool_input", {}).get("command")
        or payload.get("toolInput", {}).get("command")
        or ""
    )
    compact = re.sub(r"\s+", " ", command.strip())

    blocked = [
        (r"\brm\s+-rf\s+/(?:\s|$)", "Refuses recursive deletion from filesystem root."),
        (r"\brm\s+-rf\s+\$HOME(?:\s|/|$)", "Refuses recursive deletion of home directory."),
        (r"\bgit\s+reset\s+--hard\b", "Refuses destructive git reset without explicit human approval."),
        (r"\bgit\s+clean\s+-fdx\b", "Refuses destructive git clean without explicit human approval."),
        (r"\bgit\s+push\b.*\s--force(?:-with-lease)?\b", "Refuses force push without explicit human approval."),
        (r"\bdrop\s+database\b", "Refuses destructive database command."),
        (r"\btruncate\s+table\b", "Refuses destructive database command."),
        (r"\bchmod\s+-R\s+777\b", "Refuses broad unsafe permission change."),
    ]

    for pattern, reason in blocked:
        if re.search(pattern, compact, re.IGNORECASE):
            print(json.dumps({"decision": "block", "reason": reason}))
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
