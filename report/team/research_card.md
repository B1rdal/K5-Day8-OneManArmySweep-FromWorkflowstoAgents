# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 — failure taxonomy: diagnose the supplied swarm's seed-55 error. |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri et al., Why Do Multi-Agent LLM Systems Fail?, NeurIPS 2025, peer-reviewed empirical trace analysis: [official proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html). |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | MAST identifies failures under system design, inter-agent misalignment, and task verification. This gives a vocabulary for diagnosing failures; it does not establish that adding agents improves this lab. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | The paper analyzes traces from seven MAS frameworks, across coding, math, and general-agent tasks. Our seeded shipping-refund simulator is outside that evaluated setting; applying its taxonomy here is an interpretation, not a replicated paper result. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Expected from the documented reference weakness, not preregistered: enforce structured order delay instead of the ticket override, holding topology constant. Predict 69/70 -> 70/70 public passes, pass^5 13/14 -> 14/14, and zero seed variance. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Both arms share bonus/verification_ablation.py::_run. The only intervention is verify_order: it blocks the seed-dependent ticket-delay override. Fix MockLLM prompts, tool definitions, topology, 14 claims, seeds 11/22/33/44/55, as_of, prices, and evaluator. Use fresh SQLite per trial. The control matches all RunResult fields except identity/path against the supplied swarm on all 70 public trials. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Interpret C-002/seed-55 as incorrect verification of task evidence: order says 2 days, ticket says 5, and the unverified arm wrongly pays 20000 VND. Measure paired pass changes, pass^5, seed variance, simulated cost/success, and tool/model counts. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `..\.venv\Scripts\python.exe -m bonus.verification_ablation --out reports/ablation.json` (PowerShell, working directory src/).
- Run id / file report: `R-swarm_unverified-C-002-s55` and `R-swarm_verified-C-002-s55`; `src/reports/ablation.json`, 140 paired-arm trials in total.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: supported on this public corpus. Unverified: 69/70, pass rate 0.985714, pass^5 0.928571, variance 0.0008163265, cost/success 49.566957 VND. Verified: 70/70, pass rate 1, pass^5 1, variance 0, cost/success 48.715714 VND. Exactly one paired trial changed pass/fail: C-002 at seed 55. Average model calls remain 3 in each arm; total simulated cost changes from 3420.12 to 3410.10 VND because the corrected branch avoids recomputation and changes the draft's token count. The cost change is a consequence of the verification intervention, not a separately adjusted treatment.
- Giới hạn: MockLLM is not a production model; latency is unavailable. This is a known seeded failure, not a discovery of its frequency in real systems. No significance claim is made from one changed trial. The ablation supports evidence verification, not a causal conclusion about swarm versus workflow topology. This is the required research exercise; no bonus credit is claimed.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
