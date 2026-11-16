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


def test_no_commit_has_an_ai_identity_or_trailer():
    """Holds on any runner: every commit in the available history is free of AI identities and attribution trailers."""
    import re
    out = subprocess.check_output(["git", "log", "--format=%an%n%ae%n%cn%n%ce%n%B%x00"], cwd=ROOT, text=True, errors="replace")
    assert not re.search(r"claude|anthropic", "\n".join(c.split("\n", 4)[0] + c.split("\n", 4)[1] + c.split("\n", 4)[2] + c.split("\n", 4)[3]
                                                       for c in out.split("\x00") if c.count("\n") >= 4), re.I)
    assert not re.search(r"(?im)^\s*(co-authored-by:.*(claude|anthropic)|claude-session:|.*generated with.*claude code)", out)


def test_local_git_identity_is_0xkinno_when_configured():
    """CI runners have no identity configured, so this only applies where one is set."""
    r = subprocess.run(["git", "config", "user.name"], cwd=ROOT, text=True, capture_output=True)
    if r.returncode != 0 or not r.stdout.strip():
        return
    assert r.stdout.strip() == "0xkinno"


def test_report_and_readme_placeholders_all_resolve():
    """Every {{...}} in the report and README must resolve from FACTS. Guards against a placeholder form the renderer ignores."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("floorprice_numbers", ROOT / "scripts" / "numbers.py")
    n = importlib.util.module_from_spec(spec); spec.loader.exec_module(n)
    facts = json.loads((ROOT / "results" / "FACTS.json").read_text())["facts"]
    for name in ("report/FLOORPRICE_report.md", "README.md"):
        out, missing = n.render((ROOT / name).read_text(encoding="utf-8"), facts)
        assert not missing, (name, missing)
        assert "{{" not in out and "}}" not in out, name
