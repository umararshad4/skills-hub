"""AC3: dangerous-command guard blocks destructive commands structurally."""
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GUARD_PATH = REPO / "claude" / "hooks" / "scripts" / "guard-dangerous-command.py"


def load_guard():
    loader = importlib.machinery.SourceFileLoader("guardmod", str(GUARD_PATH))
    spec = importlib.util.spec_from_loader("guardmod", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


guard = load_guard()


class TestBlocks(unittest.TestCase):
    BLOCKED = [
        "rm -rf /",
        "rm -rf /*",
        "rm -rf ~",
        "rm -rf $HOME",
        "rm -fr /etc",
        "rm --recursive --force /",
        "rm -r -f /var/data",
        "sudo rm -rf /usr",
        "mkfs.ext4 /dev/sda1",
        "dd if=/dev/zero of=/dev/sda",
        "find / -delete",
        "chmod -R 777 /",
        "git reset --hard",
        "git reset --hard HEAD~3",
        "git clean -fdx",
        "git push --force",
        "git push origin main -f",
        ":(){ :|:& };:",
        "echo data > /dev/sda",
        'bash -c "rm -rf /"',
        "sh -c 'rm -rf /etc'",
        'eval "rm -rf $HOME"',
        'bash -c "sudo rm -rf /usr"',
    ]

    def test_destructive_commands_are_blocked(self):
        for cmd in self.BLOCKED:
            with self.subTest(cmd=cmd):
                self.assertIsNotNone(guard.dangerous_reason(cmd), f"should block: {cmd}")


class TestAllows(unittest.TestCase):
    ALLOWED = [
        "git status",
        "ls -la",
        'echo "never run rm -rf /"',          # dangerous text as data, not a command
        "rm -rf node_modules",                  # relative project path
        "rm -rf ./build",
        "rm -rf dist",
        "rm file.txt",                          # not recursive+force
        "git push --force-with-lease",          # the safe variant
        "git clean -n",                          # dry run
        "find . -name '*.pyc' -delete",         # relative path
        "chmod 644 file.txt",
        "dd if=in.img of=out.img",              # not a device
        "cat /dev/null",
        'bash -c "ls -la"',                      # benign interpreter payload
        "sh -c 'npm run build'",
        'eval "echo hello"',
    ]

    def test_benign_commands_are_allowed(self):
        for cmd in self.ALLOWED:
            with self.subTest(cmd=cmd):
                self.assertIsNone(guard.dangerous_reason(cmd), f"should allow: {cmd}")


class TestEdgeCases(unittest.TestCase):
    def test_empty_command(self):
        self.assertIsNone(guard.dangerous_reason(""))

    def test_unbalanced_quotes_fall_back_and_still_block(self):
        # shlex would raise; the raw fallback must still catch this.
        self.assertIsNotNone(guard.dangerous_reason('rm -rf / "'))

    def test_chained_destructive_command_is_blocked(self):
        self.assertIsNotNone(guard.dangerous_reason("cd /tmp && rm -rf /etc"))


if __name__ == "__main__":
    unittest.main()
