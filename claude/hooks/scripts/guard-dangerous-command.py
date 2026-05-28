#!/usr/bin/env python3
"""PreToolUse guard for destructive Bash commands.

Tokenizes the command (respecting quotes and shell operators) and inspects the
actual command name + arguments, so dangerous words used as *data* are not
blocked while real destructive commands are — including ones hidden behind
interpreter wrappers (`bash -lc`, `sh -ec`), git global options
(`git --no-pager reset --hard`), and pipes (`xargs rm -rf`).

This is a best-effort SAFETY NET, not a sandbox. It cannot catch every
obfuscation (e.g. runtime variable indirection `a=/; rm -rf $a`, base64-decoded
payloads). Treat a pass as "no obvious destructive pattern", not "proven safe".
"""
import json
import re
import shlex
import sys

HOME_PREFIXES = ("~", "$HOME", "${HOME}")
INTERPRETERS = {"bash", "sh", "zsh", "dash", "ksh", "fish", "ash"}
# git global options that take a value (consume the following token).
GIT_VALUE_OPTS = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--super-prefix"}
DANGEROUS_RM_TARGETS = {"/", "/*", "*", ".", "..", "./", "/.", "/*/"}
# Raw block devices (write here destroys a disk). Matches /dev/sda, /dev/rdisk0, etc.
DEVICE_RE = re.compile(r"/dev/(r?disk\d|sd[a-z]|nvme\d|hd[a-z]|vd[a-z]|mmcblk\d|loop\d)", re.IGNORECASE)
PROTECTED_WRITE_RE = re.compile(r"/(etc/(passwd|shadow|sudoers|hosts)|boot/)", re.IGNORECASE)


def _is_abs_or_home(target: str) -> bool:
    return target.startswith("/") or target.startswith(HOME_PREFIXES)


def _split_segments(tokens: list[str]) -> list[list[str]]:
    operators = {";", "|", "||", "&&", "&", "(", ")", "\n", "<", ">", ">>", ">|", "|&"}
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


def _rm_is_destructive(args: list[str], stdin_fed: bool = False) -> bool:
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
    # Fed by a pipe/xargs (targets arrive on stdin) — recursive force rm is unsafe.
    if stdin_fed and not targets:
        return True
    return any(target in DANGEROUS_RM_TARGETS or _is_abs_or_home(target) for target in targets)


def _git_subcommand_args(args: list[str]) -> list[str]:
    """Strip leading git global options to find the real subcommand + its args."""
    i = 0
    while i < len(args):
        a = args[i]
        if a in GIT_VALUE_OPTS:
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        return args[i:]
    return []


def _git_is_destructive(args: list[str]) -> str | None:
    sub = _git_subcommand_args(args)
    if not sub:
        return None
    if sub[0] == "reset" and "--hard" in sub:
        return "Refuses destructive git reset --hard without explicit human approval."
    if sub[0] == "clean":
        flags = "".join(a[1:] for a in sub if a.startswith("-") and not a.startswith("--"))
        if "f" in flags and "d" in flags:
            return "Refuses destructive git clean -fd[x] without explicit human approval."
    if sub[0] == "push":
        if "--force" in sub or any(a.startswith("-") and not a.startswith("--") and "f" in a[1:] for a in sub):
            return "Refuses git push --force without explicit human approval (use --force-with-lease)."
    return None


def _interp_inline_command(segment: list[str]) -> str | None:
    """If a segment is an interpreter invoked with -c (possibly bundled flags like
    -lc/-ec/-xc), return the inline command string it would run."""
    for i, tok in enumerate(segment):
        if tok.rsplit("/", 1)[-1] not in INTERPRETERS:
            continue
        for j in range(i + 1, len(segment)):
            a = segment[j]
            if a == "-c" or (a.startswith("-") and not a.startswith("--") and "c" in a[1:]):
                return segment[j + 1] if j + 1 < len(segment) else None
            if a.startswith("-"):
                continue
            break  # a non-flag operand before any -c means a script path, not inline
    return None


def dangerous_reason(command) -> str | None:
    """Return a block reason if the command is destructive, else None."""
    if isinstance(command, (list, tuple)):
        command = " ".join(str(part) for part in command)
    if not isinstance(command, str) or not command.strip():
        return None
    compact = re.sub(r"\s+", " ", command.strip())
    nospace = compact.replace(" ", "")

    if ":(){" in nospace and ":|:" in nospace:
        return "Refuses fork bomb."

    # Redirects to a raw device or a protected system file (reliable on raw text).
    redirect = re.search(r"(?:>\||>>?)\s*(\S+)", compact)
    while redirect:
        target = redirect.group(1)
        if DEVICE_RE.search(target):
            return "Refuses writing directly to a raw block device."
        if PROTECTED_WRITE_RE.search(target):
            return "Refuses overwriting a protected system file."
        redirect = re.search(r"(?:>\||>>?)\s*(\S+)", compact[redirect.end():])

    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return _raw_fallback(compact)

    segments = _split_segments(tokens)
    for seg_index, segment in enumerate(segments):
        # Recurse into interpreter / eval payloads.
        inline = _interp_inline_command(segment)
        if inline:
            inner = dangerous_reason(inline)
            if inner:
                return inner
        for i, token in enumerate(segment):
            if token.rsplit("/", 1)[-1] == "eval" and segment[i + 1:]:
                inner = dangerous_reason(" ".join(segment[i + 1:]))
                if inner:
                    return inner

        fed_by_pipe = seg_index > 0
        for idx, token in enumerate(segment):
            base = token.rsplit("/", 1)[-1]
            args = segment[idx + 1:]

            if base == "rm" and _rm_is_destructive(args, stdin_fed=fed_by_pipe or "xargs" in segment[:idx]):
                return "Refuses recursive force deletion of an absolute, home, or root path."
            if base == "xargs":
                # xargs rm -rf <stdin> — targets come from the pipe, treat as unsafe.
                rest = segment[idx + 1:]
                if rest and rest[0].rsplit("/", 1)[-1] == "rm" and _rm_is_destructive(rest[1:], stdin_fed=True):
                    return "Refuses xargs rm -rf fed from a pipe."
            if base.startswith("mkfs") or base in ("wipefs", "blkdiscard", "shred"):
                if base != "shred" or any(DEVICE_RE.search(a) for a in args):
                    return f"Refuses destructive disk operation ({base})."
            if base == "dd" and any(a.startswith("of=") and DEVICE_RE.search(a) for a in args):
                return "Refuses dd writing to a device."
            if base == "tee" and any(DEVICE_RE.search(a) for a in args):
                return "Refuses tee to a raw block device."
            if base == "find" and "-delete" in args and any(
                _is_abs_or_home(a) for a in args if not a.startswith("-")
            ):
                return "Refuses find -delete over an absolute/home/root path."
            if base in ("chmod",) and ("-R" in args or "--recursive" in args) and any(
                a.endswith("777") or a == "000" for a in args
            ):
                return "Refuses broad unsafe recursive permission change (chmod -R 777)."
            if base in ("chown", "chgrp") and ("-R" in args or "--recursive" in args) and any(
                t in DANGEROUS_RM_TARGETS or (_is_abs_or_home(t) and len(t.rstrip("/").split("/")) <= 2)
                for t in args if not t.startswith("-")
            ):
                return f"Refuses recursive ownership change of a system root ({base} -R)."
            if base == "git":
                reason = _git_is_destructive(args)
                if reason:
                    return reason

    return None


def _raw_fallback(compact: str) -> str | None:
    patterns = [
        (r"\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*[rR]|--recursive\s+--force)\b.*\s(/|~|\$HOME|/\*)", "Refuses recursive force deletion of a dangerous path."),
        (r"\bmkfs|\bwipefs|\bblkdiscard", "Refuses destructive disk operation."),
        (r"\bdd\b.*\bof=/dev/", "Refuses dd writing to a device."),
        (r"\bgit\b.*\breset\s+--hard\b", "Refuses destructive git reset --hard."),
        (r"\bgit\b.*\bclean\s+-[a-zA-Z]*f[a-zA-Z]*d", "Refuses destructive git clean."),
        (r"\bgit\b.*\bpush\b.*(--force\b|\s-[a-zA-Z]*f\b)", "Refuses git push --force."),
        (r"\bchmod\s+-R\s+777\b", "Refuses broad unsafe permission change."),
        (r"(?:>>?|>\|)\s*/dev/(r?disk|sd|nvme|hd|vd|mmcblk|loop)", "Refuses writing to a raw block device."),
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
    try:
        reason = dangerous_reason(command)
    except Exception:
        # A guard bug must never crash the tool call; fail open but stay silent.
        return 0
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
