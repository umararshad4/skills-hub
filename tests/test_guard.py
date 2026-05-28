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
        # Audit-reproduced bypasses (bundled interpreter flags):
        'bash -lc "rm -rf /"',
        'bash -cx "rm -rf /"',
        'bash -xc "rm -rf /"',
        "sh -ec 'rm -rf /'",
        'zsh -lc "rm -rf /"',
        # git global options before the subcommand:
        "git --no-pager reset --hard",
        "git -c core.pager=cat clean -fd",
        "git -C /repo reset --hard",
        # device / protected writes the operator/regex set missed:
        "echo x | tee /dev/sda",
        "echo x > /dev/rdisk0",
        "echo x >| /dev/sda",
        "wipefs /dev/sda",
        "shred /dev/sda",
        # broad destructive forms:
        "chown -R root:root /",
        "find /Users | xargs rm -rf",
        "echo '' > /etc/passwd",
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
        'bash -lc "ls -la"',                     # bundled flags, benign payload
        "git -C /repo status",                   # git global opt, benign subcommand
        "git --no-pager log",
        "chown -R me:me ./dist",                 # recursive chown of a relative path
        "tee out.log",                           # tee to a normal file
        "shred ./secret.txt",                    # shred a file (not a device)
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

    def test_non_string_command_does_not_crash(self):
        # A list payload must be analyzed, not raise.
        self.assertIsNotNone(guard.dangerous_reason(["rm", "-rf", "/"]))
        self.assertIsNone(guard.dangerous_reason(["ls", "-la"]))
        self.assertIsNone(guard.dangerous_reason(None))


if __name__ == "__main__":
    unittest.main()
