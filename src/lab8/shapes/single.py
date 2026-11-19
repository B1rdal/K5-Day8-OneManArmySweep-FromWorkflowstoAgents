"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from typing import Any

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed,
            status=status, proposal_amount=proposal, budget=budget,
            trace=trace, error_reason=reason,
        )

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        trace.add("claim", {"found": claim["found"], "has_order": bool(claim.get("order_id"))})
        if not claim["found"]:
            return done("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return done("needs_info", reason="missing_order_id")

        # MockLLM emits text, not structured tool calls. This bounded adapter
        # selects the next read from observations; no generated text sets money.
        state: dict[str, Any] = {}

        def decide(seen: dict[str, Any]) -> dict[str, Any]:
            last_tool = seen.get("last_tool")
            if last_tool:
                state[last_tool] = seen["last_result"]
                trace.add("observation", {"tool": last_tool})
            complete(budget, seed=seed, purpose="decide", prompt=f"refund read step; last_tool={last_tool}")
            trace.add("model", {"purpose": "decide"})

            if "lookup_order" not in state:
                return {"tool": "lookup_order", "args": {
                    "order_id": claim["order_id"], "principal_id": claim["principal_id"],
                }}
            order_view = state["lookup_order"]
            if not order_view["visible"]:
                return {"final": {"status": "escalated", "error_reason": order_view["reason"]}}
            if "lookup_policy" not in state:
                return {"tool": "lookup_policy", "args": {}}
            if "compute_compensation" not in state:
                return {"tool": "compute_compensation", "args": {"order": order_view["order"]}}
            return {"final": {"status": "ready"}}

        loop = run_react(
            conn, budget,
            observation={"claim": {"order_id": claim["order_id"]}},
            decide=decide, max_steps=8, worker=True,
        )
        if loop["stopped"] == "step_cap":
            return done("failed", reason="step_cap")
        final = loop["final"]
        if final["status"] == "escalated":
            return done("escalated", reason=final["error_reason"])
        quote = state.get("compute_compensation")
        if final["status"] != "ready" or quote is None:
            return done("failed", reason="missing_quote")

        # Only the deterministic read tool's result can propose an amount.
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)
        if proposal <= 0:
            return done("denied", reason=quote["reason"])
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"]})
        if not outcome["ok"]:
            return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
        return done("resolved", proposal)
    finally:
        try:
            trace.write()
        finally:
            conn.close()
