# Lab 8 — implemented work and review guide

This is an AI-assisted working draft. Review the code and explain it yourself
before submitting. The team is **OneManArmySweep**, with one member:
**Đào Đức Sơn**, student ID **2A202604105**, credited with all project contributions
with Codex assistance disclosed. Final review and an implementation commit are pending.
The solo report draft is available at
`report/team/2A202604105_DaoDucSon.md`; the original individual template is preserved.

## What is ready

- `src/lab8/shapes/workflow.py`: fixed read, scope, quote, and host-write steps.
- `src/lab8/shapes/single.py`: bounded read-only ReAct adapter, at most 8 decisions.
- `src/lab8/shapes/orchestrator.py`: allowlisted handoff and read-only investigator.
- `src/tests/test_student_safety.py`: extra integration checks for the student shapes.
- `src/bonus/verification_ablation.py` and `src/tests/test_bonus_verification.py`:
  required R2 research exercise, with no bonus credit claimed.
- Generated benchmark, crash, and ablation JSON in `src/reports/`.
- Draft group report, architecture decision, and research card in `report/team/`.

The supplied host, evaluator, configs, data, and reference swarm are unchanged.

## Measured results

Validation environment: Windows AMD64, CPython 3.13.18, pytest 8.4.2,
PyYAML 6.0.3. Runs completed on 2026-11-17; the lab policy date remains
the supplied `as_of` value, 2026-11-15.

- Initial smoke: pass; initial host tests: 54 passed.
- Completed student matrix: 248 passed, including the swarm's expected miss.
- Final combined suite: **402 passed**, including 100 added checks.
- Host crash suite: **20/20**. Extra tests exercise all three crash windows
  through every student shape and verify crash exceptions actually fire.
- Benchmark: workflow, single, and orchestrator each pass **70/70** public trials;
  reference swarm passes **69/70**. Each shape sees 14 claims and five seeds.
- Workflow has the lowest simulated cost/success: **27.86 VND**, compared with
  38.28 for single, 47.77 for orchestrator, and 49.57 for reference swarm.
- Research: structured-order verification raises the paired swarm arm from
  69/70 to 70/70. Both arms have three model calls per trial on average.
- Submission checker: **1 FAIL, 1 WARN**. The remaining failure is the empty
  implementation commit hash. The contribution table now credits the sole member
  and passes. The warning reports uncommitted changes. All implementation,
  evidence, and research checks pass.

Public results do not establish the required hidden pass rate. No hidden corpus
or instructor labels were supplied, and no hidden result has been fabricated.

## Run it on this machine

The working environment is `.venv` at the repository root. From PowerShell:

```powershell
Set-Location 'F:\Github\K5-Day8-OneManArmySweep-FromWorkflowstoAgents\src'
..\.venv\Scripts\python.exe -m lab8.smoke
..\.venv\Scripts\python.exe -m pytest -q -o addopts=
```

The second command runs both host and student tests; the default pytest command
excludes the student matrix. To run just a single claim:

```powershell
..\.venv\Scripts\python.exe -m lab8.run --shape workflow --claim-id C-014 --seed 11 --db data/student-example.sqlite
```

C-014 proposes the full 150000 VND entitlement; the host pays only the 120000 VND
remaining after the seeded 30000 VND shipping refund. Running again on the same
database must preserve the original effect and its single committed audit.

To regenerate all measured evidence, still from `src/`:

```powershell
..\.venv\Scripts\python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
..\.venv\Scripts\python.exe -m lab8.crash_test --count 20 --out reports/crash.json
..\.venv\Scripts\python.exe -m bonus.verification_ablation --out reports/ablation.json
..\.venv\Scripts\python.exe -m lab8.check_submission
```

Do not edit the generated JSON. Its run IDs use the starter's deterministic
`R-<shape>-<claim>-s<seed>` format, so they identify a trial but not a unique
execution timestamp. Use a real implementation commit to establish provenance.

If the environment must be recreated, run from the repository root:

```powershell
uv venv --python 3.13 .venv
uv pip install --python .venv\Scripts\python.exe -r src\requirements.txt
```

The machine's registered `py -3.13` points at a missing installation. Explicitly
using the working environment avoids that stale entry and requires no script
execution-policy change.

## Explain these decisions before submitting

1. **Why quote the full amount?** The host subtracts refunds paid by other
   claims on the same order. Subtracting in the shape first would subtract twice.
2. **Who chooses the money?** `compute_compensation`, using structured order
   fields and current effective policy. Generated text cannot set an amount.
3. **Who can write?** Only the shape's host call, after reads/investigation. The
   ReAct runtime and investigator enforce a read-only tool list. Approval belongs
   to the exact claim and is checked by the unchanged host.
4. **Why is retry safe?** The host transaction commits one refund row and one
   audit with unique keys. A retry consults that ledger; a checkpoint alone is
   insufficient. A different computed amount becomes a conflict.
5. **Why omit the raw ticket from traces?** User text can contain secrets, private
   data, and instructions. Student traces record only minimal typed outcomes,
   deterministic quotes, and sanitized handoffs. They never dump parent context.
6. **Is the single agent choosing tools through a real model?** No. The provided
   MockLLM returns text, so a bounded Python adapter maps observations to read
   actions and budgets each simulated model call. Production tool selection and
   language understanding are outside this lab's evidence.
7. **Do 11 trace events violate the 8-step ReAct cap?** No. The cap limits decision
   iterations. Trace events also include observations, quotes, and host outcomes.
   They are different units. Sparse reference traces also make cross-shape step
   counts unsuitable as proof of runtime efficiency.
8. **What did the ablation establish?** With the same swarm code, prompts, and
   inputs, blocking its documented ticket-delay override fixes C-002/seed-55.
   This supports verification of evidence in this simulator; it does not prove
   that one topology is generally superior. The unverified control is checked
   against all 70 reference trials.

## Finish the submission

1. Your full name and student ID are recorded. Add your email and GitHub profile
   to `TEAM.md` and your individual report when available.
   The required repo name is `K5-L3A-DAY08-OneManArmySweep-FromWorkflowsToAgents`.
   Ensure GitHub naming/access meets SUBMISSION.md.
2. Review and understand the implementation. The contribution table credits
   all solo project work to Đào Đức Sơn, names both added test files, and discloses
   Codex assistance. Add the actual implementation commit reference once created.
3. Complete your final review and self-assessment in
   `report/team/2A202604105_DaoDucSon.md`.
   Keep the original `report/team/MSSV_HoTen.md` template.
4. When supplied, run the documented `student_drop/` self-check. Unlabeled
   self-checks cannot produce a hidden pass rate; instructor grading is separate.
5. Commit reviewed implementation/tests/evidence. Put that actual commit hash
   in `decision_adr.md` and `group_report.md`, and actual contribution commit/test
   references in `TEAM.md`. Then commit the completed documentation.
6. Rerun the submission checker until it reports `0 FAIL`. Push the reviewed
   work, then submit the solo repository link on LMS using your own account.

Git commit, push, repository renaming, and LMS submission have not been performed.
