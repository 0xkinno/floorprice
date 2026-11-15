import pytest

from floorprice import llm, prompts
from floorprice.budget import Budget, BudgetExceeded
from floorprice.cache import Cache

GOOD = {"output": [{"type": "reasoning", "content": [{"type": "output_text", "text": "SECRET"}]},
                   {"type": "message", "content": [{"type": "output_text", "text": '{"score": 80, "label": "reliable", "reason": "x"}'}]}],
        "usage": {"input_tokens": 10, "output_tokens": 5}, "status": "completed"}


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("ADAPTION_API_KEY", "test-key")
    monkeypatch.delenv("FLOORPRICE_OFFLINE", raising=False)
    monkeypatch.setattr(llm, "PACE_S", 0.0)


def mk(tmp_path, cap=100):
    return Cache(tmp_path / "raw"), Budget(path=tmp_path / "b.json", cap=cap, per_call=1.0)


def test_reasoning_items_are_skipped(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "_post", lambda *a, **k: GOOD)
    c, b = mk(tmp_path)
    r = llm.call("m", "s", "u", cache=c, budget=b)
    assert "SECRET" not in r["text"] and prompts.parse_rating(r["text"])["score"] == 80


def test_cache_replay_and_no_duplicate_calls(tmp_path, monkeypatch):
    n = {"c": 0}

    def fake(*a, **k):
        n["c"] += 1
        return GOOD
    monkeypatch.setattr(llm, "_post", fake)
    c, b = mk(tmp_path)
    llm.call("m", "s", "u", cache=c, budget=b)
    c2 = Cache(tmp_path / "raw")           # restart: new process reads the file
    r = llm.call("m", "s", "u", cache=c2, budget=b)
    assert n["c"] == 1 and r["cached"]


def test_offline_mode_replays_and_refuses_misses(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "_post", lambda *a, **k: GOOD)
    c, b = mk(tmp_path)
    llm.call("m", "s", "u", cache=c, budget=b)
    monkeypatch.setenv("FLOORPRICE_OFFLINE", "1")
    monkeypatch.setattr(llm, "_post", lambda *a, **k: (_ for _ in ()).throw(AssertionError("network used")))
    assert llm.call("m", "s", "u", cache=c, budget=b)["cached"]
    with pytest.raises(RuntimeError, match="offline"):
        llm.call("m", "s", "other", cache=c, budget=b)


def test_budget_stops_before_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "_post", lambda *a, **k: GOOD)
    c, b = mk(tmp_path, cap=2)
    llm.call("m", "s", "1", cache=c, budget=b)
    llm.call("m", "s", "2", cache=c, budget=b)
    with pytest.raises(BudgetExceeded):
        llm.call("m", "s", "3", cache=c, budget=b)
    assert b.state["calls"] == 2
    assert Budget(path=tmp_path / "b.json", cap=2).state["calls"] == 2   # persisted


def test_empty_message_is_flagged_not_dropped(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "_post", lambda *a, **k: {"output": [{"type": "reasoning"}], "usage": {}})
    c, b = mk(tmp_path)
    r = llm.call("m", "s", "u", cache=c, budget=b)
    assert r["error"] == "empty_message" and prompts.parse_rating(r["text"])["parse"] == "fail"


def test_sample_index_changes_key(tmp_path):
    k0 = llm.request_key("m", "s", "u", 0.7, 600, 0)[1]
    k1 = llm.request_key("m", "s", "u", 0.7, 600, 1)[1]
    assert k0 != k1


def test_parse_rating_cases():
    p = prompts.parse_rating
    assert p('{"score": 101}')["parse"] == "fail"
    assert p('```json\n{"score": 5, "label": "unreliable"}\n```')["score"] == 5
    assert p('text "score": 33 more')["parse"] == "regex"
    assert p("")["parse"] == "fail"
    assert p('{"score": true}')["parse"] == "fail"
