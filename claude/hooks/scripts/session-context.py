#!/usr/bin/env python3
import json
from pathlib import Path


def main() -> int:
    home = Path.home()
    guide = home / ".claude" / "CLAUDE.md"
    mct_guide = home / ".claude" / "MCT.md"
    text = ""
    if guide.exists():
        text = guide.read_text(errors="ignore")[:6000]
    if mct_guide.exists():
        text += "\n\n## MCT Routing Guide\n\n" + mct_guide.read_text(errors="ignore")[:8000]

    context = (
        "Global engineering context loaded from ~/.claude/CLAUDE.md.\n\n"
        + text
        if text
        else "Global engineering context: inspect the repo first, keep changes scoped, and run targeted checks."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
