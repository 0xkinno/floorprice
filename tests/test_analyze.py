"""Pipeline test on a SYNTHETIC fixture written to a temp dir. Test data only; never written to results/."""
import json

import numpy as np

from floorprice import analyze, experiments as E
from floorprice.floor import INF


def write(tmp, exp, model, rows):
    with open(tmp / f"{exp}__{model}.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def fixture(tmp, model="mA"):
    rng = np.random.default_rng(0)
    e1 = [{"exp": "E1", "model": model, "item": it["item"], "domain": it["domain"], "pc1": it["meta"]["pc1"], "decile": it["meta"]["decile"],
           "score": float(np.clip(it["meta"]["pc1"] * 100 + rng.normal(0, 8), 0, 100)), "label": "mixed", "parse": "json"} for it in E.items("E1")]
    write(tmp, "E1", model, e1)
    e2 = [{"exp": "E2", "model": model, "item": it["item"], "domain": it["domain"], **it["meta"],
           "score": 50.0 + (8 if it["meta"]["token"] != "none" else 0) + rng.normal(0, 2), "label": "unknown", "parse": "json"} for it in E.items("E2")]
    write(tmp, "E2", model, e2)
    base = {}
    e3 = []
    for it in E.items("E3"):
        v = it["meta"]["variant"]
        sc = {"control": 20, "A3_boilerplate": 40, "A4_endorsement": 60, "A5_injection": 90, "combined": 95}[v]
        e3.append({"exp": "E3", "model": model, "item": it["item"], "domain": it["domain"], **it["meta"], "score": float(sc), "label": "mixed", "parse": "json"})
    write(tmp, "E3", model, e3)
    e3h = [{"exp": "E3h", "model": model, "item": it["item"], "domain": it["domain"], **it["meta"], "score": 30.0, "label": "mixed", "parse": "json"} for it in E.items("E3h")]
    write(tmp, "E3h", model, e3h)
    e4 = [{"exp": "E4", "model": model, "item": it["item"], "domain": it["domain"], "sample": s, "score": 50 + rng.normal(0, 5), "label": "mixed", "parse": "json"}
          for it in E.items("E4") for s in range(3)]
    write(tmp, "E4", model, e4)
    e5 = [{"exp": "E5", "model": model, "item": it["item"], **it["meta"], "text": it["page"].replace("voted", "decided").replace("said", "stated"), "empty": False} for it in E.items("E5")]
    write(tmp, "E5", model, e5)


def test_pipeline_runs_and_hypotheses_follow_the_fixture(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    fixture(main)
    A = analyze.run(main_dir=main, sims_dir=tmp_path / "sims", out=tmp_path / "a.json", ev_dir=tmp_path / "ev", models=["mA"])
    h = A["hypotheses"]
    assert h["H1"]["supported"] and h["H1"]["rho"] > 0.9
    assert h["H2"]["pooled_mean_paired_difference"] > 0
    pm = A["llm"]["per_model"]["mA"]
    assert pm["E3_floor_tokens"]["0.5"] != INF       # A4 reaches 60 vs threshold around 0.7? see below
    assert "sims t4" in A["pending"] and any("coder1" in p for p in A["pending"])
    assert A["e5"]["pairs"] > 0


def test_missing_models_are_pending_not_defaulted(tmp_path):
    A = analyze.run(main_dir=tmp_path, sims_dir=tmp_path, out=tmp_path / "a.json", ev_dir=tmp_path, models=["mX"])
    assert "E1 mX" in A["pending"] and A["hypotheses"] == {} or "H1" not in A["hypotheses"]
