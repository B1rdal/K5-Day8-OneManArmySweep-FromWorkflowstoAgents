"""R2 ablation: toggle only whether a swarm trusts ticket delay over the order.

Adapted from the provided lab8.shapes.swarm_reference. Both arms use the same
implementation, model prompts, tools, seeds, corpus, and evaluator. Verification
blocks the reference's intentional order override; it does not change approvals.

Run from src/: python -m bonus.verification_ablation --out reports/ablation.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lab8.app import register_extra_shapes
from lab8.benchmark import render_table, run_benchmark
from lab8.config_loader import repo_path
from lab8.console import utf8_stdio
from lab8.db import connect, load_json, load_jsonl
from lab8.durability import issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace


def run_verified(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult:
    return _run(claim_id, seed=seed, store_path=store_path, crash_at=crash_at, verify_order=True)


def run_unverified(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult:
    return _run(claim_id, seed=seed, store_path=store_path, crash_at=crash_at, verify_order=False)


def _run(claim_id: str, *, seed: int, store_path: str, crash_at: str | None, verify_order: bool) -> RunResult:
    shape = "swarm_verified" if verify_order else "swarm_unverified"
    conn = connect(store_path)
    budget = Budget()
    trace = Trace(make_run_id(shape, claim_id, seed))

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        return finish(
            conn, shape=shape, claim_id=claim_id, seed=seed,
            status=status, proposal_amount=proposal, budget=budget,
            trace=trace, error_reason=reason,
        )

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        if not claim["found"]:
            trace.add("error", {"reason": "unknown_claim"})
            return done("failed", reason="unknown_claim")

        complete(budget, seed=seed, purpose="peer", prompt=claim["ticket"])
        parsed_delay = parse_delay_days(claim["ticket"])
        complete(budget, seed=seed, purpose="parse", prompt=claim["ticket"])
        if not claim.get("order_id"):
            complete(budget, seed=seed, purpose="draft", prompt="needs_info")
            trace.add("decision", {"status": "needs_info"})
            return done("needs_info", reason="missing_order_id")

        handoff = make_handoff(
            request_id=f"REQ-{claim_id}", claim_id=claim_id,
            task="check_applicable_policy", facts={},
            allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
        )
        trace.add("handoff", handoff)
        investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
        order_view = investigated["tools"].get("lookup_order", {})
        trace.add("investigator", {
            "lookup_order": order_view,
            "policy_count": len(investigated["tools"].get("lookup_policy", {}).get("policies", [])),
        })
        if not order_view.get("visible"):
            complete(budget, seed=seed, purpose="draft", prompt="escalated")
            return done("escalated", reason=order_view.get("reason"))

        order = dict(order_view["order"])
        # The sole intervention. All other code is shared by both arms.
        if not verify_order and parsed_delay is not None and parsed_delay != int(order["delay_days"]) and seed % 5 == 0:
            order["delay_days"] = parsed_delay
            trace.add("model_override", {"delay_days": parsed_delay})
        quote = investigated["tools"]["compute_compensation"]
        if order["delay_days"] != order_view["order"]["delay_days"]:
            budget.add_tool(tool_cost())
            quote = compute_compensation(conn, order)
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)
        complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
        if proposal <= 0:
            return done("denied", reason=quote["reason"])

        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        if not outcome["ok"]:
            return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
        return done("resolved", proposal)
    finally:
        try:
            trace.write()
        finally:
            conn.close()


def main() -> int:
    utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="reports/ablation.json")
    args = parser.parse_args()
    register_extra_shapes([
        "swarm_unverified=bonus.verification_ablation:run_unverified",
        "swarm_verified=bonus.verification_ablation:run_verified",
    ])
    report = run_benchmark(
        world=load_json(repo_path("data", "public_world_state.json")),
        claims=load_jsonl(repo_path("data", "public_claims.jsonl")),
        shapes=["swarm_unverified", "swarm_verified"], seeds=[11, 22, 33, 44, 55],
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(render_table(report))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
