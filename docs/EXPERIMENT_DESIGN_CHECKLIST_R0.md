# SattvaRoute Pre-Experiment Design Checklist

- **Task:** T-SKILL-003 — controlled methodology integration of catalog entry PS-001
  (`k-dense-ai/scientific-agent-skills@experimental-design`).
- **Status:** DRAFT methodology template — available for use in FDE planning, **not an installed
  skill and not an active project gate**. All five catalog entries remain `RECOMMENDED` pending
  explicit adoption authorization (user instruction, 2026-11-23).
- **Scope:** converts the *methodology* (Fisher's principles and structural-error checks) into a
  SattvaRoute-specific pre-run checklist. It does **not** install the upstream skill and does **not**
  copy its scripts, `uv/pip` installation, network calls, `Write/Bash` tool grants or CSV outputs.
- **Governance:** this checklist is subordinate to `AGENTS.md`, `PROJECT_STATE.md`, D-007
  (report-level verification), the approval gate (`scripts/sattva_approval.py`) and scratch
  isolation. It never authorizes a remedy, run, DRC waiver or production change.

## Source and attribution

- Upstream: `K-Dense-AI/scientific-agent-skills`, skill `experimental-design`, version **1.5**
  (last reviewed 2026-09-30), MIT. Pinned at commit `c21d13b3cc2894680229ba9959a53281acb9200e`.
- SKILL.md (read-only, fetched for this integration):
  `https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/c21d13b3cc2894680229ba9959a53281acb9200e/skills/experimental-design/SKILL.md`
- Verbatim principles retained: randomization, replication, blocking/local control; pseudoreplication;
  confounding by nuisance variables; "no proper control"; "Pre-specify the analysis"; run-order
  randomization; document design/versions/seed. SattvaRoute-specific translations below are marked
  **INFERRED** where they extend the upstream text.
- Upstream citation (for provenance, not a license requirement here): Kassis, T., Agarwal, V., He,
  Y., Patel, D., & Brueckner, A. M. (2026). *Scientific Agent Skills: A Library of Procedural
  Knowledge for Research Agents.* arXiv:2609.00065. https://doi.org/10.48550/arXiv.2609.00065

---

## A. Pre-run gate — answer every question before an experiment is approved

| # | Check | Verbatim principle | SattvaRoute translation | PASS condition |
|---|---|---|---|---|
| A1 | **State the question, unit and response** | "State the question, the unit, and the response. What is randomized? What is measured? At what level is a true independent replicate?" | **INFERRED:** Question = e.g. "does freeing M4 OBS corridor X create ≥3 accepted APs?" Unit = **one isolated run with one fixed configuration**, not one DRC marker or one AP candidate. Response = accepted AP count, sparse threshold, DRT codes, stage rc, artifact hashes. | All three written explicitly before the run. |
| A2 | **Replication at the correct level** | "Replication — independent repetition at the right level"; "pseudoreplication: counting repeated measurements on the same unit as independent replicates" | **INFERRED:** 9 AP candidates or 107 markers from one ODB are repeated measurements of ONE run. They cannot count as 9 experiments. Independent replicates require separate run IDs with the same configuration or a properly randomized multi-run plan. | Replicate count stated as number of independent runs; no marker/candidate counted as a replicate. |
| A3 | **Proper concurrent control** | "No proper control. Without a concurrent control ... you can't separate the treatment effect from time, placebo, or handling effects." | **INFERRED:** A remedy arm needs a same-binary, same-ODB, same-config **concurrent no-op control arm** differing only in the intended variable. **FDE-006U did NOT have one** — its `prod == olddiag == newdiag_off` three-way equivalence was an *instrumentation behavior-neutrality* check (all three arms kept the original OBS), and section 10 of the FDE-006U report explicitly records "no no-op control arm" as a residual gap. Do not cite that check as satisfying A3. A prior historical run is not a concurrent control. | A genuine no-op arm is planned with identical toolchain/config and only the approved variable changed; if none, state the gap explicitly and STOP. |
| A4 | **Single variable** | "No analysis can rescue a confounded ... design after the fact." | **INFERRED:** Only ONE approved delta (e.g. M4 OBS corridor geometry). No simultaneous LEF + config + binary + placement change. Exact modification digest recorded. | One variable; all other inputs pinned and hashed. |
| A5 | **Nuisance factors blocked or held constant** | "Blocking / local control — group similar units ... remove nuisance variation" | **INFERRED:** Block/hold constant: OpenROAD binary SHA, source ODB SHA, LEF/GDS/Lib hashes, config.mk + SDC + PDN hashes, D-014 patch presence, WSL memory/swap, supervisor/process mode, run ID scheme, time window. If multiple arms run, interleave or randomize run order. | Every named nuisance factor either blocked, interleaved, or explicitly justified as constant. |
| A6 | **Randomized run order when multiple arms** | "Randomize run/processing order ... defeat drift"; "use a seeded schedule and follow it" | **INFERRED:** Assign arm order with a recorded deterministic rule (e.g. `sha256(decision_id + run_tag)` sort), not "control first, remedy second" convenience. Record the rule and resulting order. | Order rule and resulting order recorded before execution. |
| A7 | **No aliasing of remedy families** | "Aliasing ignored in fractional designs ... know your alias structure before concluding a factor has no effect." | **INFERRED:** Parameter variations of the same remedy family (FDE-007 R1-N x3534–3672 and R1-N-W x3474–3672) are ONE factor at two levels, not two independent confirmations. The KB family key is authoritative. | Family declared; variations labelled levels, not replicates or independent families. |
| A8 | **Pre-specify the analysis and acceptance bar** | "Pre-specify the analysis"; "document the design, software versions, seed, and schedule" | **INFERRED:** Before execution write: accepted-AP threshold, sparse threshold, required absent DRT codes, stage rc expectations, DRC/extraction/timing disposition labels (PASS/FAIL/INCONCLUSIVE/BLOCKED/NOT_RUN), and the exact hashes to be captured. | Acceptance criteria and outcome labels fixed in the approval record; no post-hoc redefinition. |
| A9 | **Report-level verification, not exit code** | Upstream: "No analysis can rescue a confounded or pseudoreplicated design after the fact." (SattvaRoute translation below is **INFERRED**; D-007 is project policy, not upstream wording.) | **INFERRED:** Plan to verify stage logs, artifacts, error census and hashes. `rc=0` alone is never PASS. | Evidence checklist present; D-007 review explicitly scheduled. |
| A10 | **Edge/position effects considered** | "Edge/position effects on plates ... Randomize or block sample positions" | **INFERRED:** For pin-access work, record pin coordinates/layers and macro-edge position; if testing many pins, block by pin row/edge strip rather than treating all pins as exchangeable. | Pin/edge stratification recorded or justified as not applicable. |
| A11 | **Feasibility and model rank** | "Confirm all settings are feasible ... intended model matrix has full rank" | **INFERRED:** Confirm every planned run uses available disk/RAM, a unique run ID, an isolated scratch directory, and no protected path write. | Feasibility check PASS; no protected path in the run plan. |
| A12 | **Baseline immutability and scratch isolation** | Upstream: "Document the design, software versions, seed, and schedule." (Project-specific controls below are **INFERRED**.) | **INFERRED:** Verify `sattva_kb.py verify-immutable` is PASS (9/9 protected artifacts), the source baseline run/ODB hashes are recorded and unchanged, and all remedy work targets a new isolated `experiments/.../scratch_design` directory. | Immutable manifest PASS, baseline ODB hash matches, scratch path declared; never write to `benchmark/`, `runs/`, `tools/` or production LEF. |

**GATE RULE:** if any A1–A12 is NO, STOP. Do not launch a run or amend the remedy without a new
decision and approval gate.

---

## B. Evidence fields to capture per arm (before and after)

| Field | Why (upstream principle) |
|---|---|
| Run ID, timestamp, arm label, planned order | design schedule / documentation |
| Exact command line and tool invocation | reproducibility |
| Binary SHA-256, OpenROAD source commit, ORFS commit | software versions |
| Source ODB, LEF, GDS, Liberty, config.mk, SDC, PDN hashes | hold-constant / block verification |
| Patch or geometry delta digest; approval ID and decision ID | single variable / controlled change |
| Nuisance-factor table (A5) and order rule (A6) | confounding control |
| Pre-specified acceptance bar (A8) | pre-specified analysis |
| Stage rc list, error census (DRT codes), accepted AP count, sparse count | response measurement |
| Artifact manifest with SHA-256 and stage logs | report-level verification (D-007) |
| Actual outcome label and reviewer findings | honest classification |
| Deviations from the pre-registered plan | no post-hoc rescue |

## C. Anti-patterns mapped to SattvaRoute history

| Upstream structural error | SattvaRoute occurrence | Required handling |
|---|---|---|
| Pseudoreplication | counting 9 FlexPA candidates or 107 marker records as independent evidence | count independent runs only |
| No proper control | early remedy attempts without a concurrent no-op arm | no-op arm mandatory (A3) |
| Confounding by nuisance | binary/config/ODB changes between arms | pin and hash all inputs (A4/A5) |
| Aliasing | R1-N and R1-N-W treated as two families | one family, two levels (A7) |
| Convenience assignment | always running control first | deterministic order rule (A6) |
| Analysis after the fact | defining success after seeing DRT-0073 disappear | pre-register bar (A8) |
| Optimizing without curvature | parameter tweaks called "validation" | each new geometry is a new approved experiment |

## D. Exclusions (what this checklist must never do)

- Never install, import or execute the upstream skill, its scripts, `uv/pip` commands, network fetches
  or CSV outputs.
- Never modify `AGENTS.md`, approval policy, runner, KB records or any protected artifact.
- Never run EDA or start a physical-design experiment by itself.
- Never define or auto-assign PASS; D-007 report-level human review remains binding.
- Never change catalog statuses from `RECOMMENDED` without explicit user adoption authorization.

## E. Usage

Use this checklist when preparing an FDE experiment proposal, before the approval gate. Record the
completed A1–A12 answers in the experiment's approval evidence. Status remains DRAFT methodology
reference until the user authorizes adoption of PS-001; using it for planning does not install or
activate the external skill.
