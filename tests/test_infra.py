import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_style  # noqa: E402
import prereg_lock  # noqa: E402


def test_style_checker_catches_each_violation():
    assert check_style.scan_text("a — b", "x")
    assert check_style.scan_text("a – b", "x")
    assert check_style.scan_text("a seamless thing", "x")
    assert check_style.scan_text("fine \U0001F600", "x")
    assert not check_style.scan_text("plain text, with commas.", "x")


def test_repo_text_is_clean():
    assert check_style.main() == 0


def test_lock_detects_change(tmp_path, monkeypatch):
    lock = prereg_lock.compute()
    assert lock["combined"] and "HYPOTHESES.md" in lock["files"]
    assert "floorprice/prompts.py" in lock["files"] and "data/prices.yaml" in lock["files"]


def test_commit_hook_blocks_attribution(tmp_path):
    msg = tmp_path / "m"
    msg.write_text("work\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n")
    hook = ROOT / ".githooks" / "commit-msg"
    assert subprocess.run([str(hook), str(msg)], cwd=ROOT).returncode != 0
    msg.write_text("work\n")
    assert subprocess.run([str(hook), str(msg)], cwd=ROOT).returncode == 0


def test_git_identity_is_0xkinno():
    name = subprocess.check_output(["git", "config", "user.name"], cwd=ROOT, text=True).strip()
    assert name == "0xkinno"
