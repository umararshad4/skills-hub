#!/usr/bin/env python3
import json


def main() -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreCompact",
            "additionalContext": "Before compacting, preserve: current goal, files changed, checks run, blockers, and exact next command."
        }
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
