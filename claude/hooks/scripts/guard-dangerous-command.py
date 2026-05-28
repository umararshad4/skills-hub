#!/usr/bin/env python3
"""PreToolUse guard for destructive Bash commands.

Tokenizes the command (respecting quotes and shell operators) and inspects the
actual command name + arguments, instead of substring-matching the raw text.
That way `echo "never run rm -rf /"` is allowed (the rm is data, not a command)
while `rm -fr /etc`, `rm --recursive --force /`, and friends are blocked.
"""
import json
import re
import shlex
import sys

HOME_PREFIXES = ("~", "$HOME", "${HOME}")
# rm targets that are catastrophic regardless of being absolute.
DANGEROUS_RM_TARGETS = {"/", "/*", "*", ".", "..", "./", "/.", "/*/"}


def _is_abs_or_home(target: str) -> bool:
    return target.startswith("/") or target.startswith(HOME_PREFIXES)


def _split_segments(tokens: list[str]) -> list[list[str]]:
    """Split a token stream into command segments on shell operators."""
    operators = {";", "|", "||", "&&", "&", "(", ")", "\n", "<", ">", ">>"}
    segments: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in operators:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


def _rm_is_destructive(args: list[str]) -> bool:
    recursive = force = False
    targets: list[str] = []
    for arg in args:
        if arg in ("--recursive", "--recursive=true"):
            recursive = True
        elif arg == "--force":
            force = True
        elif arg.startswith("--"):
            continue
        elif arg.startswith("-") and len(arg) > 1:
            flags = arg[1:]
            if "r" in flags or "R" in flags:
                recursive = True
            if "f" in flags:
                force = True
        else:
            targets.append(arg)
    if not (recursive and force):
        return False
    return any(target in DANGEROUS_RM_TARGETS or _is_abs_or_home(target) for target in targets)


def _git_is_destructive(args: list[str]) -> str | None:
    joined = " ".join(args)
    if args[:2] == ["reset", "--hard"] or (args[:1] == ["reset"] and "--hard" in args):
        return "Refuses destructive git reset --hard without explicit human approval."
    if args[:1] == ["clean"]:
        flags = "".join(a[1:] for a in args if a.startswith("-") and not a.startswith("--"))
        if "f" in flags and "d" in flags:
            return "Refuses destructive git clean -fd[x] without explicit human approval."
    if args[:1] == ["push"]:
        if "--force" in args or any(a.startswith("-") and not a.startswith("--") and "f" in a[1:] for a in args):
            return "Refuses git push --force without explicit human approval (use --force-with-lease)."
    return None


def dangerous_reason(command: str) -> str | None:
    """Return a block reason if the command is destructive, else None."""
    if not command or not command.strip():
        return None
    compact = re.sub(r"\s+", " ", command.strip())

    # Fork bomb — structural signature, hard to express via tokens.
    if ":(){" in compact.replace(" ", "") and ":|:" in compact.replace(" ", ""):
        return "Refuses fork bomb."

    # Tokenize respecting quotes and shell operators. On a parse error fall back
    # to conservative raw checks so we never fail open.
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return _raw_fallback(compact)

    # Redirect to a raw block device, e.g. `> /dev/sda`.
    for i, token in enumerate(tokens):
        if token in (">", ">>") and i + 1 < len(tokens):
            if re.match(r"/dev/(sd|nvme|hd|disk|mmcblk|vd)", tokens[i + 1]):
                return "Refuses writing directly to a raw block device."

    for segment in _split_segments(tokens):
        # Scan every token as a possible command name so leading wrappers (sudo,
        # env VAR=val, nice, xargs, ...) don't hide the real command. Quoted text
        # stays a single token, so dangerous words used as *data* never match.
        for idx, token in enumerate(segment):
            base = token.rsplit("/", 1)[-1]
            args = segment[idx + 1:]

            if base == "rm" and _rm_is_destructive(args):
                return "Refuses recursive force deletion of an absolute, home, or root path."
            if base.startswith("mkfs"):
                return "Refuses filesystem format (mkfs)."
            if base == "dd" and any(a.startswith("of=/dev/") for a in args):
                return "Refuses dd writing to a device."
            if base == "find" and "-delete" in args and any(
                _is_abs_or_home(a) for a in args if not a.startswith("-")
            ):
                return "Refuses find -delete over an absolute/home/root path."
            if base == "chmod" and ("-R" in args or "--recursive" in args) and any(
                a.endswith("777") or a == "000" for a in args
            ):
                return "Refuses broad unsafe recursive permission change (chmod -R 777)."
            if base == "git":
                reason = _git_is_destructive(args)
                if reason:
                    return reason

    return None


def _raw_fallback(compact: str) -> str | None:
    patterns = [
        (r"\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*[rR]|--recursive\s+--force|--force\s+--recursive)\b.*\s(/|~|\$HOME|/\*)", "Refuses recursive force deletion of a dangerous path."),
        (r"\bmkfs", "Refuses filesystem format (mkfs)."),
        (r"\bdd\b.*\bof=/dev/", "Refuses dd writing to a device."),
        (r"\bgit\s+reset\s+--hard\b", "Refuses destructive git reset --hard."),
        (r"\bgit\s+clean\s+-[a-zA-Z]*f[a-zA-Z]*d", "Refuses destructive git clean."),
        (r"\bgit\s+push\b.*(--force\b|\s-[a-zA-Z]*f\b)", "Refuses git push --force."),
        (r"\bchmod\s+-R\s+777\b", "Refuses broad unsafe permission change."),
        (r">\s*/dev/(sd|nvme|hd|disk|mmcblk|vd)", "Refuses writing to a raw block device."),
    ]
    for pattern, reason in patterns:
        if re.search(pattern, compact, re.IGNORECASE):
            return reason
    return None


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
    reason = dangerous_reason(command)
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
