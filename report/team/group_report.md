# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: OneManArmySweep; this report is an AI-assisted draft for review.
- Thành viên: Đào Đức Sơn — 2A202604105 (sole member; see `TEAM.md`).
- Commit chốt (trùng `report/team/decision_adr.md`): pending an implementation commit; the current working changes are uncommitted.

## 2. Mục tiêu và cách tiếp cận

Process the same synthetic LogiX-VN refund claims using fixed workflow, bounded single-agent, orchestrator/investigator, and the supplied reference swarm. Select the least autonomous implementation that meets the task and safety requirements. This is a solo submission by OneManArmySweep. Đào Đức Sơn is the sole project contributor, covering implementation, integration, tests, evaluation, research, and reports. The work was completed with Codex assistance, disclosed in the individual report.

## 3. Giải pháp

**Workflow:** read the safe claim view, require the structured order ID, look up the order under its owner, and compute compensation using the current effective policy. Missing IDs become needs_info; inaccessible/missing orders become escalated; zero entitlement is denied. Positive full quotes go to the host without subtracting prior refunds.

**Single:** use run_react(max_steps=8, worker=True). A bounded Python adapter selects read tools based on observations: order, current policy, compensation, then final. Every model call is charged to Budget. MockLLM produces text rather than structured actions, so this demonstrates loop composition and access control, not autonomous production-model tool selection. Money comes only from the deterministic compensation tool. The refund write runs after the loop.

**Orchestrator:** construct an allowlisted handoff with empty facts and only lookup_order, lookup_policy, and compute_compensation. The investigator receives no write registry. The orchestrator reads the verified quote and alone reaches the host write gate.

All three use the supplied finish helper for ledger-backed results. Approval, per-order caps, and transaction/idempotency enforcement remain in the unchanged host. The full quote avoids double-subtracting prior refunds, especially T14. InjectedCrash propagates; finally flushes a safe trace and closes the database. Traces contain minimal outcomes and deterministic quotes, never raw tickets, headers, secrets, or personal order fields. See the ADR for exact trace contents.

## 4. Kết quả

Measured on Windows AMD64 with CPython 3.13.18, pytest 8.4.2, and PyYAML 6.0.3. Each shape ran 14 public claims across seeds 11, 22, 33, 44, 55 using fresh stores, the supplied prices, and as_of 2026-11-15. Figures below come from `src/reports/benchmark.json`.

| Shape | Pass | Pass^5 | Seed min–max | Variance | Cost/success, simulated VND | Mean/p95 trace events |
| --- | --- | --- | --- | --- | --- | --- |
| workflow | 70/70 (1.000000) | 1.000000 | 1.000000–1.000000 | 0 | 27.86 | 4.43 / 5 |
| single | 70/70 (1.000000) | 1.000000 | 1.000000–1.000000 | 0 | 38.28 | 9.71 / 11 |
| orchestrator | 70/70 (1.000000) | 1.000000 | 1.000000–1.000000 | 0 | 47.77 | 7.14 / 8 |
| swarm | 69/70 (0.985714) | 0.928571 | 0.928571–1.000000 | 0.000816327 | 49.57 | 2.80 / 3 |

The one benchmark failure is `R-swarm-C-002-s55`: the supplied reference trusts five days in the ticket over two days in the order. Student shapes use the order. The public matrix intentionally asserts this swarm miss, so a green test suite does not imply a perfect swarm benchmark.

The supplied crash suite reports **20/20** in `src/reports/crash.json`. Additional integration tests run all three crash windows through every student shape and check resume/retry, immutable committed amounts on conflict, approval caps and borrowed approvals, missing order IDs, sensitive ticket text, the ReAct cap, and read-only handoffs. The research-control tests compare all 70 public trials against the reference. Final combined validation is recorded in the walkthrough.

The research ablation holds the swarm implementation and prompts fixed, changing only whether ticket delay can override order delay. Verification changes 69/70 to 70/70 and cost/success from 49.57 to 48.72 simulated VND. The only changed pass/fail is C-002/seed-55. Details and run IDs are in the research card and `src/reports/ablation.json`. Hidden data was not supplied, so no hidden score is claimed.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

The registered `py -3.13` entry pointed to missing `F:\Python\python.exe` and failed with 0x80070003. A working CPython 3.13.18 environment was created at the repository root with `uv venv --python 3.13 .venv`, then dependencies were installed with `uv pip install --python .venv\Scripts\python.exe -r src\requirements.txt`. Commands run from src/ use the explicit `..\.venv\Scripts\python.exe` path, requiring no activation policy change.

The first research CLI run wrote its report but failed printing Vietnamese text under Windows cp1252. Adding the supplied utf8_stdio helper to that CLI fixed the output; the experiment was rerun successfully. No host, evaluator, pricing, or fixture files were changed.

## 6. Tổng hợp đóng góp

Đào Đức Sơn (2A202604105), the sole member, is credited with all project contributions: the three student shapes, integration, safety tests, benchmark/crash evaluation, controlled R2 experiment, architecture decision, and reports. Added tests are `src/tests/test_student_safety.py` and `src/tests/test_bonus_verification.py`. Codex assistance is disclosed in `TEAM.md` and `report/team/2A202604105_DaoDucSon.md`. Implementation commit references, final review, and the member's self-assessment remain pending.

## 7. Hạn chế và hướng cải thiện

MockLLM is not a production model; latency is unavailable. Main-benchmark prompts and model/tool call counts differ, so architecture-wide cost differences do not isolate topology. Trace-event counts depend on instrumentation and are not comparable runtime operations. Cost accounting follows the reference and excludes the common host write path. Zero observed public failures is not proof of general safety or of the >=0.75 hidden threshold. Reconsider the workflow only when representative held-out tasks show a meaningful quality benefit for bounded agents under the same safety and cost constraints. Review, commit provenance, team reports, hidden checks when available, and GitHub/LMS submission remain outstanding.

## 8. Tài liệu tham khảo

1. Repository starter, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, and `docs/metrics.md`.
2. Cemri et al. (NeurIPS 2025), [Why Do Multi-Agent LLM Systems Fail?](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html). Used as a taxonomy for interpretation, not as evidence for this simulator's performance.
3. Generated evidence: `src/reports/benchmark.json`, `src/reports/crash.json`, `src/reports/ablation.json`. The ablation control is adapted from the supplied `swarm_reference.py` and validated against it.
