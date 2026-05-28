"""Load the extension-less `claude/bin/mct` script as an importable module.

The CLI ships as a single stdlib-only script with a `if __name__ == "__main__"`
guard, so importing it here only defines its functions/classes without running
`main()`.
"""
import importlib.machinery
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MCT_PATH = REPO_ROOT / "claude" / "bin" / "mct"


def load_mct():
    loader = importlib.machinery.SourceFileLoader("mctcli", str(MCT_PATH))
    spec = importlib.util.spec_from_loader("mctcli", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


mct = load_mct()
