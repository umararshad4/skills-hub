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


def opensrc_context(start: Path) -> str:
    root = start.resolve()
    for path in [root, *root.parents]:
        package_json = path / "package.json"
        if package_json.exists():
            manifest = path / "opensrc" / "manifest.json"
            if manifest.exists():
                return (
                    "\n\n## opensrc Status\n\n"
                    f"Found package.json at `{package_json}` and opensrc manifest at `{manifest}`. "
                    "Run `mct start --md`, read opensrc/manifest.json, verify that every declared package is represented, "
                    "then read or fill task-relevant opensrc/packages/*.md files from official sources before planning."
                )
            return (
                "\n\n## opensrc Status\n\n"
                f"Found package.json at `{package_json}` but no `opensrc/manifest.json`. "
                "First run `mct opensrc --fetch-metadata`, confirm every declared dependency is represented, "
                "then fill task-relevant package context from official source-of-truth docs before normal MCT task execution."
            )
        if (path / ".git").exists():
            break
    return "\n\n## opensrc Status\n\nNo package.json found from the current working directory."


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

    cwd = payload_cwd(payload)
    todo = find_todo(cwd)
    activation = (
        "## MCT Activation Contract\n\n"
        "The user explicitly requested MCT. Do not treat this as optional context and do not answer from memory. "
        "Make MCT visible to the user: your first progress update should say `MCT toolkit active` and summarize the current step. "
        "Before editing or giving a final answer, run or emulate these steps in order:\n\n"
        "1. Read AGENTS.md plus README.md, claude/MCT.md, and claude/CLAUDE.md when present.\n"
        "2. Run `mct start --md` when the CLI is available, otherwise manually apply the same checklist.\n"
        "3. If package.json exists, run `mct opensrc --fetch-metadata` before planning, and ensure opensrc covers every declared package.\n"
        "4. Deep-fill official source context for libraries relevant to the current task before editing.\n"
        "5. If TODO.md exists, run `mct status --md` and `mct next --claim` before editing.\n"
        "6. Run verification before `mct done`, record concrete checks or skipped-check reasons, then run `mct final-check --todo-log` before stopping.\n\n"
        "If any step cannot run, state the exact blocker and continue with the closest manual equivalent.\n\n"
    )
    context = activation + "Apply this routing guide:\n\n" + mct + opensrc_context(cwd) + todo_context(todo)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context
        }
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
