#!/bin/bash
# Publish ONLY T-SKILL-001 text artifacts from D:\SattvaRoute to
# D:\SattvaRoute_publish. Explicit allowlist, blocklist and post-copy SHA-256.
# Does not modify or replace scripts/publish_kb.sh or any T-KB-001 implementation.
set -euo pipefail

SRC=${SATTVA_SRC:-/mnt/d/SattvaRoute}
PUB=${SATTVA_PUB:-/mnt/d/SattvaRoute_publish}

ALLOW=(
  ".skills/README.md"
  ".skills/INVENTORY.md"
  ".skills/DISCOVERY_REPORT.md"
  ".skills/EVALUATION_SUMMARY.md"
  ".skills/SECURITY_AUDIT.md"
  ".skills/INSTALLATION_REPORT.md"
  ".skills/skill_sources.json"
  ".skills/validate_skills.py"
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
  "docs/SKILL_FINAL_REPORT.md"
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
