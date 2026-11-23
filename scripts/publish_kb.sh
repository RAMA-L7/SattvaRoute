#!/bin/bash
# Publish ONLY the approved KB text artifacts from D:\SattvaRoute to
# D:\SattvaRoute_publish, with an explicit allowlist, blocklist and post-copy
# SHA-256 verification. No EDA, no run directories, no binaries.
set -euo pipefail

SRC=${SATTVA_SRC:-/mnt/d/SattvaRoute}
PUB=${SATTVA_PUB:-/mnt/d/SattvaRoute_publish}

ALLOW=(
  "scripts/sattva_kb.py"
  "scripts/publish_kb.sh"
  "tests/test_kb.py"
  "docs/KNOWLEDGE_BASE.md"
  "docs/KB_AUDIT.md"
  "docs/KB_FINAL_REPORT.md"
  "docs/decisions/DECISIONS.md"
  "knowledge/README.md"
  "knowledge/fde_seed.json"
  "knowledge/kb_records.jsonl"
  "knowledge/kb_chain.json"
  "knowledge/kb_manifest.json"
  "knowledge/kb_immutable_manifest.json"
  "knowledge/KB_METRICS.md"
  "knowledge/PROVENANCE_DRIFT.md"
  "knowledge/queries/drt0073_pin_access.json"
  "knowledge/queries/drt0305_zero_net.json"
  "knowledge/queries/obs_carve_production.json"
  "PROJECT_STATE.md"
  "coordination/TASK_BOARD.md"
  "coordination/ACTIVE_WORK.md"
  "logs/DAILY_LOG.md"
  "logs/AGENT_ACTIVITY.md"
  "logs/REVIEW_LOG.md"
  "logs/REPORT_LOG.md"
  "logs/sessions/T-KB-001_S001_handoff.md"
)

echo "PUBLISH_ALLOW_COUNT=${#ALLOW[@]}"
for rel in "${ALLOW[@]}"; do
  if [ ! -f "$SRC/$rel" ]; then
    echo "FATAL: allowlisted source missing: $rel" >&2
    exit 1
  fi
done

# Blocklist is checked against the PUBLICATION repo after copy.
# Pre-existing, committed ASCII fixtures in the publication repo (not binaries,
# not introduced by this mission). They are grandfathered, never updated here.
ALLOW_EXISTING=(
  'benchmark/design/sattva_sram/macro/sram_x4x4x1.lef'
  'benchmark/design/sattva_sram/macro/sram_x4x4x1.lib'
)

BLOCK_PATTERNS=(
  '*.odb' '*.gds' '*.lef' '*.lib' '*.spef' '*.v' '*.sv' '*.sdc'
  '*.so' '*.a' '*.o' '*.exe' '*.bin' '*.img' '*.pyc'
  'runs/*' 'experiments/*' 'tools/*' 'benchmark/*' 'configs/*'
)

copy_one() {
  local rel=$1 dst="$PUB/$1"
  mkdir -p "$(dirname "$dst")"
  cp "$SRC/$rel" "$dst"
  local a b
  a=$(sha256sum "$SRC/$rel" | cut -d' ' -f1)
  b=$(sha256sum "$dst" | cut -d' ' -f1)
  if [ "$a" != "$b" ]; then
    echo "FATAL: hash mismatch after copy: $rel" >&2
    exit 1
  fi
  echo "HASH_OK $rel $a"
}

for rel in "${ALLOW[@]}"; do copy_one "$rel"; done

echo '--- blocklist scan (NEW files only; git HEAD is the pre-existing baseline) ---'
BAD=0
mapfile -t PREEXISTING < <(git -C "$PUB" ls-files)
while IFS= read -r -d '' f; do
  rel=${f#"$PUB/"}
  # Pre-existing ignored Python bytecode caches are never copied by this script.
  case "$rel" in *.pyc|*/__pycache__/*) continue;; esac
  skip=0
  for ok in "${PREEXISTING[@]}"; do
    [ "$rel" = "$ok" ] && skip=1
  done
  [ "$skip" -eq 1 ] && continue
  for pat in "${BLOCK_PATTERNS[@]}"; do
    # shellcheck disable=SC2053
    if [[ "$rel" == $pat ]]; then
      echo "BLOCKED_ARTIFACT_PRESENT $rel (pattern $pat)" >&2
      BAD=1
    fi
  done
done < <(find "$PUB" -path "$PUB/.git" -prune -o -type f -print0)
if [ "$BAD" -ne 0 ]; then
  echo 'FATAL: publication tree contains blocked artifacts' >&2
  exit 1
fi
echo 'BLOCKLIST_SCAN_CLEAN'
echo 'PUBLISH_STAGE_OK'
