"""Credit budget. Reads the cap from FLOORPRICE_CREDIT_CAP, keeps a running total in results/budget.json."""
import json
import os
import threading
from pathlib import Path

BUDGET_FILE = Path(__file__).resolve().parent.parent / "results" / "budget.json"


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    """Credits per call come from the usage object when the API reports one; otherwise from
    FLOORPRICE_CREDITS_PER_CALL, which scripts/probe.py measures and prints."""

    def __init__(self, path=None, cap=None, per_call=None):
        self.path = Path(path) if path else BUDGET_FILE
        self.cap = float(cap if cap is not None else os.getenv("FLOORPRICE_CREDIT_CAP", "875"))
        self.per_call = float(per_call if per_call is not None else os.getenv("FLOORPRICE_CREDITS_PER_CALL", "0.01"))
        self._lock = threading.Lock()
        self.state = {"credits": 0.0, "calls": 0, "tokens_in": 0, "tokens_out": 0}
        if self.path.exists():
            self.state.update(json.loads(self.path.read_text()))

    def check_or_raise(self):
        with self._lock:
            if self.state["credits"] + self.per_call > self.cap:
                raise BudgetExceeded(f"credit cap {self.cap} reached at {self.state['credits']:.2f}")

    def record(self, usage):
        usage = usage or {}
        credits = usage.get("credits") if "credits" in usage else None
        if credits is None:
            credits = usage.get("credit_cost")
        if credits is None:
            credits = usage.get("cost")   # the Responses API reports cost per call; it matches the credit price table
        with self._lock:
            self.state["credits"] += float(credits) if credits is not None else self.per_call
            self.state["calls"] += 1
            self.state["tokens_in"] += int(usage.get("input_tokens") or 0)
            self.state["tokens_out"] += int(usage.get("output_tokens") or 0)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.state, indent=2))
            os.replace(tmp, self.path)
