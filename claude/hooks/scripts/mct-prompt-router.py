#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path


def payload_cwd(payload: dict) -> Path:
    candidates = [
        payload.get("cwd"),
        payload.get("currentWorkingDirectory"),
        payload.get("workspace_dir"),
        payload.get("workspaceDir"),
    ]
    for candidate in candidates:
        if candidate:
            path = Path(str(candidate)).expanduser()
            if path.exists():
                return path
    return Path(os.getcwd())


def find_todo(start: Path) -> Path | None:
    current = start.resolve()
    for path in [current, *current.parents]:
        todo = path / "TODO.md"
        if todo.exists() and todo.is_file():
            return todo
        if (path / ".git").exists():
            break
    return None


def todo_context(todo_path: Path | None) -> str:
    if not todo_path:
        return (
            "\n\n## TODO.md Status\n\n"
            "No root TODO.md was found from the current working directory. Continue normal MCT routing."
        )

    text = todo_path.read_text(errors="ignore")
    preview = text[:8000]
    return (
        "\n\n## TODO.md Status\n\n"
        f"Found TODO.md at `{todo_path}`. Treat it as the project task queue. "
        "Read the full file before editing, classify unchecked items, then complete sequentially or in a safe parallel batch.\n\n"
        "Preview:\n\n"
        "```markdown\n"
        + preview
        + ("\n...\n" if len(text) > len(preview) else "\n")
        + "```"
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    prompt = (
        payload.get("prompt")
        or payload.get("user_prompt")
        or payload.get("userPrompt")
        or ""
    )

    if not re.search(r"\bMCT\b|my claude toolkit|use mct|mct mode", prompt, re.IGNORECASE):
        return 0

    mct_path = Path.home() / ".claude" / "MCT.md"
    if mct_path.exists():
        mct = mct_path.read_text(errors="ignore")[:12000]
    else:
        mct = "MCT requested: inspect repo, classify task, route to correct skills/subagents/checks, and finish with a completion receipt."

    todo = find_todo(payload_cwd(payload))
    context = "The user requested MCT. Apply this routing guide:\n\n" + mct + todo_context(todo)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context
        }
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
