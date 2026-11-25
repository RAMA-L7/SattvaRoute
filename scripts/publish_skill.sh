#!/bin/bash
# Publish ONLY T-SKILL-001 text artifacts from D:\SattvaRoute to
# D:\SattvaRoute_publish. Explicit allowlist, blocklist and post-copy SHA-256.
# Does not modify or replace scripts/publish_kb.sh or any T-KB-001 implementation.
set -euo pipefail

SRC=${SATTVA_SRC:-/mnt/d/SattvaRoute}
PUB=${SATTVA_PUB:-/mnt/d/SattvaRoute_publish}

ALLOW=(
  "knowledge/kb_records.jsonl"
  "knowledge/remedy_ledger.jsonl"
  "knowledge/remedy_seed.jsonl"
  "config/remedy_budgets.json"
  "config/sattva_manifest.json"
  "scripts/remedy_engine.py"
  "scripts/remedy_kb.py"
  "scripts/run_baseline_orfs.sh"
  "scripts/sattva_approval.py"
  "state/approval_policy.json"
  "scripts/manifest.py"
  "scripts/diagnosis_agent.py"
  "scripts/pnr_cli.py"
  "scripts/compare_runs.py"
  "scripts/seed_remedy_kb.py"
  "scripts/run_remedy_demo.py"
  "tests/test_recovery_cli.py"
  "docs/ARCHITECTURE.md"
  "docs/IMPLEMENTATION_GAPS.md"
  "docs/CONTROL_BENCHMARK_SELECTION.md"
  "docs/BENCHMARK_PREPARATION.md"
  "docs/BASELINE_ACCEPTANCE_CRITERIA.md"
  "docs/RECOVERY_WORKFLOW.md"
  "docs/PIPELINE_TEST_RESULTS.md"
  "docs/PNR_FINAL_REPORT.md"
  "docs/PNR_ADJUDICATION.md"
  "docs/T1_EXPERIMENT_REPORT.md"
  "docs/T1_ADJUDICATION.md"
  "scripts/live_diagnosis.py"
  "scripts/evidence_package.py"
  "scripts/evaluate_diagnosis.py"
  "tests/test_live_diagnosis.py"
  "knowledge/kb_manifest.json"
  "knowledge/kb_chain.json"
  "knowledge/kb_immutable_manifest.json"
  ".skills/README.md"
  ".skills/INVENTORY.md"
  ".skills/DISCOVERY_REPORT.md"
  ".skills/EVALUATION_SUMMARY.md"
  ".skills/SECURITY_AUDIT.md"
  ".skills/INSTALLATION_REPORT.md"
  ".skills/skill_sources.json"
  ".skills/validate_skills.py"
  ".skills/PROJECT_SKILLS.json"
  ".skills/PROJECT_SKILLS.md"
  "scripts/publish_skill.sh"
  "docs/decisions/DECISIONS.md"
  "PROJECT_STATE.md"
  "coordination/TASK_BOARD.md"
  "coordination/ACTIVE_WORK.md"
  "logs/DAILY_LOG.md"
  "logs/AGENT_ACTIVITY.md"
  "logs/REVIEW_LOG.md"
  "logs/REPORT_LOG.md"
  "logs/sessions/T-SKILL-001_S001_handoff.md"
  "logs/sessions/T-SKILL-002_S001_handoff.md"
  "docs/SKILL_FINAL_REPORT.md"
  "docs/SKILL_RESEARCH_REPORT.md"
  "docs/EXPERIMENT_DESIGN_CHECKLIST.md"
  "docs/EXPERIMENT_DESIGN_CHECKLIST_R0.md"
  "docs/EXPERIMENT_DESIGN_CHECKLIST_R1.md"
  "docs/T-SKILL-007_CHANGE_RATIONALE.md"
  "docs/T-SKILL-007_INDEPENDENT_REVIEW.md"
  "docs/T-SKILL-007_RETROSPECTIVE_REVALIDATION.md"
  "docs/T-SKILL-007_FINAL_ADJUDICATION.md"
  "docs/T-SKILL-006_SHADOW_PROPOSAL.md"
  "docs/T-SKILL-006_SHADOW_ASSESSMENT.md"
  "docs/T-SKILL-006_SHADOW_PILOT_REPORT.md"
  "docs/T-SKILL-008_SHADOW_PROPOSAL.md"
  "docs/T-SKILL-008_SHADOW_ASSESSMENT.md"
  "docs/T-SKILL-008_INDEPENDENT_REVIEW.md"
  "docs/T-SKILL-008_FINAL_REPORT.md"
  "docs/ENG009_CURRENT_STATE_AUDIT.md"
  "docs/ENG009_DRT_FAILURE_INVENTORY.md"
  "docs/ENG009_HYPOTHESIS_MATRIX.md"
  "docs/ENG009_MEASUREMENT_CAPABILITY_REPORT.md"
  "docs/ENG009_PRIOR_EXPERIMENT_REVIEW.md"
  "docs/ENG009_NEXT_STEP_PLAN.md"
  "docs/ENG009_PROPOSED_DIAGNOSTIC_EXPERIMENT.md"
  "docs/ENG009_AGENT_FINDINGS_AND_ADJUDICATION.md"
  "docs/ENG009_FINAL_REPORT.md"
  "docs/ENG010_INSTRUMENTATION_AND_EQUIVALENCE.md"
  "docs/ENG010_STATIC_EOL_AND_GDS.md"
  "docs/ENG010_MARKER_PROVENANCE_DATASET.md"
  "docs/ENG010_SLIVER_VERDICT_AND_ROOT_CAUSE.md"
  "docs/ENG010_INDEPENDENT_REVIEW_AND_ADJUDICATION.md"
  "docs/ENG010_FINAL_REPORT.md"
  "docs/ENG010_provenance.diff.txt"
  "docs/ENG010_provenance_sample.txt"
  "docs/ENG011_GEOMETRY_RULE_CALCULATIONS.md"
  "docs/ENG011_CANDIDATE_DEFINITIONS.md"
  "docs/ENG011_DIAGNOSTIC_RESULTS.md"
  "docs/ENG011_INDEPENDENT_REVIEW_AND_ADJUDICATION.md"
  "docs/ENG011_FINAL_REPORT.md"
  "docs/ENG012_AP_SOURCE_TRACE.md"
  "docs/ENG012_BROAD_CARVE_PROVENANCE.md"
  "docs/ENG012_ARTIFACT_COMPARISON.md"
  "docs/ENG012_GENERATION_REJECTION_MATRIX.md"
  "docs/ENG012_PREDICATE_FAILURE_ANALYSIS.md"
  "docs/ENG012_INDEPENDENT_REVIEW_AND_ADJUDICATION.md"
  "docs/ENG012_HYPOTHESIS_UPDATE.md"
  "docs/ENG012_NEXT_DIAGNOSTIC_RANKING.md"
  "docs/ENG012_FINAL_REPORT.md"
  "docs/ENG013_DIRECTIONAL_PLANAR_DRC_REPORT.md"
  "docs/ENG013_PREDICATE_FAILURE_TRACE.md"
  "docs/ENG013_BLOCKER_ATTRIBUTION.md"
  "docs/ENG013_GEOMETRY_CORRELATION.md"
  "docs/ENG013_INSTRUMENTATION_NEUTRALITY.md"
  "docs/ENG013_INDEPENDENT_REVIEW_AND_ADJUDICATION.md"
  "docs/ENG013_ROOT_CAUSE_MATRIX_UPDATE.md"
  "docs/ENG013_FINAL_REPORT.md"
  "docs/ENG014_ROOT_CAUSE_RECONSTRUCTION.md"
  "docs/ENG014_EVIDENCE_VS_INFERENCE.md"
  "docs/ENG014_REMEDY_CLASS_MATRIX.md"
  "docs/ENG014_RISK_AND_VALIDATION.md"
  "docs/ENG014_INDEPENDENT_REVIEWS.md"
  "docs/ENG014_COORDINATOR_ADJUDICATION.md"
  "docs/ENG014_FINAL_REPORT.md"
  "docs/ENG015_BASELINE_RECORD.md"
  "docs/ENG015_RESEARCH_REPORT.md"
  "docs/ENG015_CANDIDATE_COMPARISON.md"
  "docs/ENG015_RESEARCH_GATE.md"
  "docs/ENG015_INDEPENDENT_REVIEWS.md"
  "docs/ENG015_COORDINATOR_ADJUDICATION.md"
  "docs/ENG015_FINAL_REPORT.md"
  "docs/WF_ARCHITECTURE_AUDIT.md"
  "docs/WF_REMEDY_FIRST_WORKFLOW.md"
  "docs/WF_AGENT_RESPONSIBILITIES.md"
  "docs/WF_REMEDY_RANKING.md"
  "docs/WF_TIME_BUDGET_AND_VALIDATION.md"
  "docs/WF_KB_EXTENSION.md"
  "docs/WF_DRT0073_DEMONSTRATION.md"
  "docs/WF_EFFICIENCY_REPORT.md"
  "docs/WF_INDEPENDENT_REVIEWS.md"
  "docs/WF_COORDINATOR_ADJUDICATION.md"
  "docs/WF_FINAL_REPORT.md"
  "docs/REPORT_INDEX.md"
  "docs/T-SKILL-005_CHECKLIST_REVISION_REPORT.md"
  "docs/T-SKILL-005_RETROSPECTIVE_COMPARISON.md"
  "docs/T-SKILL-004_RETROSPECTIVE_VALIDATION.md"
  "docs/EXPERIMENT_DESIGN_CHECKLIST_REVIEW.md"
  "logs/sessions/T-SKILL-003_S001_handoff.md"
  "logs/sessions/T-SKILL-004_S001_handoff.md"
  "logs/sessions/T-SKILL-005_S001_handoff.md"
  "logs/sessions/T-SKILL-006_S001_handoff.md"
  "logs/sessions/T-SKILL-007_S001_handoff.md"
  "logs/sessions/T-SKILL-008_S001_handoff.md"
  "logs/sessions/T-ENGINEERING-009_S001_handoff.md"
  "logs/sessions/T-ENGINEERING-010_S001_handoff.md"
  "logs/sessions/T-ENGINEERING-011_S001_handoff.md"
  "logs/sessions/T-ENGINEERING-012_S001_handoff.md"
  "logs/sessions/T-ENGINEERING-013_S001_handoff.md"
  "logs/sessions/T-ENGINEERING-014_S001_handoff.md"
  "logs/sessions/T-ENGINEERING-015_S001_handoff.md"
  "logs/sessions/T-WORKFLOW-001_S001_handoff.md"
  "logs/sessions/T-PNR-001_S001_handoff.md"
  "logs/sessions/T1-LIVE-DIAG_S001_handoff.md"
)

echo "PUBLISH_ALLOW_COUNT=${#ALLOW[@]}"
for rel in "${ALLOW[@]}"; do
  if [ ! -f "$SRC/$rel" ]; then
    echo "FATAL: allowlisted source missing: $rel" >&2
    exit 1
  fi
done

BLOCK_PATTERNS=('*.odb' '*.gds' '*.lef' '*.lib' '*.spef' '*.exe' '*.bin' '*.img' '*.pyc'
                'runs/*' 'experiments/*' 'tools/*' 'benchmark/*' 'configs/*')

copy_one() {
  local rel=$1 dst="$PUB/$1" a b
  mkdir -p "$(dirname "$dst")"
  cp "$SRC/$rel" "$dst"
  a=$(sha256sum "$SRC/$rel" | cut -d' ' -f1)
  b=$(sha256sum "$dst" | cut -d' ' -f1)
  [ "$a" = "$b" ] || { echo "FATAL: hash mismatch after copy: $rel" >&2; exit 1; }
  echo "HASH_OK $rel $a"
}

for rel in "${ALLOW[@]}"; do copy_one "$rel"; done

echo '--- blocklist scan (NEW files only; git HEAD is baseline) ---'
BAD=0
mapfile -t PREEXISTING < <(git -C "$PUB" ls-files)
while IFS= read -r -d '' f; do
  rel=${f#"$PUB/"}
  case "$rel" in *.pyc|*/__pycache__/*) continue;; esac
  skip=0
  for ok in "${PREEXISTING[@]}"; do [ "$rel" = "$ok" ] && skip=1; done
  [ "$skip" -eq 1 ] && continue
  for pat in "${BLOCK_PATTERNS[@]}"; do
    # shellcheck disable=SC2053
    if [[ "$rel" == $pat ]]; then
      echo "BLOCKED_ARTIFACT_PRESENT $rel (pattern $pat)" >&2
      BAD=1
    fi
  done
done < <(find "$PUB" -path "$PUB/.git" -prune -o -type f -print0)
[ "$BAD" -eq 0 ] || { echo 'FATAL: blocked artifacts in publication tree' >&2; exit 1; }
echo 'BLOCKLIST_SCAN_CLEAN'
echo 'PUBLISH_STAGE_OK'
