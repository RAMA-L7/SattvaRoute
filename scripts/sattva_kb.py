#!/usr/bin/env python3
"""SattvaRoute incremental engineering Knowledge Base (KB mission).

Standard library only. No database, framework, network, hosted model or new
service. Knowledge is stored as an append-oriented JSON Lines ledger, reusing
the durable-ledger / SHA-256 / strict-validation pattern of sattva_approval.py.

Design rules (enforced in code, not just documentation):
  * records are never edited or deleted; a correction is a NEW record with a
    newer record_version and a `supersedes` relationship;
  * each record carries a content hash so tampering is detectable;
  * outcome states are explicit (PASS/FAIL/INCONCLUSIVE/BLOCKED/NOT_RUN);
  * PASS is refused unless experimentally supported evidence is cited, so
    success is never inferred from missing evidence;
  * retrieval scores are decomposed into named factors and every recommendation
    traces to real record IDs and hashes;
  * applicability is classified BEFORE a remedy is recommended, and a remedy
    family that failed under comparable conditions is never promoted to
    STRONG_MATCH without documented new justification;
  * all writes are confined to the knowledge directory; protected design,
    baseline, experiment, tool and safety-policy paths are read-only.

This module does not run EDA, does not modify flow inputs and does not decide
physical correctness. It is engineering memory, not an autonomous controller.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

try:
    from sattva_approval import TargetLock  # reuse existing cross-process lock
except ImportError:  # pragma: no cover - allows standalone import in tests
    TargetLock = None

SCHEMA_VERSION = 1
OUTCOMES = ("PASS", "FAIL", "INCONCLUSIVE", "BLOCKED", "NOT_RUN")
ROOT_CAUSE_STATUS = ("ESTABLISHED", "PROBABLE", "REFUTED", "UNKNOWN")
SCOPES = ("DESIGN_SPECIFIC", "REUSABLE", "CROSS_DESIGN")
APPLICABILITY = ("STRONG_MATCH", "PARTIAL_MATCH", "INCOMPATIBLE",
                 "PREVIOUSLY_FAILED", "NO_RELEVANT_KNOWLEDGE",
                 "INSUFFICIENT_EVIDENCE")
MATURITY_MIN, MATURITY_MAX = 0, 4

# Families that are findings/diagnostics, never deployable remedies. A PASS in
# these families is evidence about the investigation, not a validated fix.
NON_REMEDY_FAMILIES = {
    "DIAGNOSTIC_ROOT_CAUSE", "CANDIDATE_DIAGNOSTIC", "DIAGNOSTIC_BUILD",
    "EVIDENCE_POLICY", "EVIDENCE_BAR", "FAILURE_VOCABULARY",
    "RUNNER_CONTRACT_VALIDATION",
}

REQUIRED_TOP = (
    "knowledge_id", "record_version", "created_at", "identity", "failure",
    "root_cause", "remedies", "experiment", "outcome", "applicability",
    "evidence", "relationships", "maturity", "provenance",
)
ALLOWED_TOP = REQUIRED_TOP + ("schema_version", "integrity", "new_justification")
# Unknown fields are rejected so that schema drift is explicit, not silent.
ALLOWED_SUB = {
    "identity": ("investigation_id", "fde_id", "experiment_ids", "design_id",
                 "design_fingerprint", "source_run", "timestamp"),
    "failure": ("category", "signature", "violation_type", "tool", "tool_version",
                "technology", "geometry", "routing_layers", "constraints", "environment",
                "pvt", "logs", "reports", "metrics"),
    "root_cause": ("status", "hypothesis", "supporting_evidence", "contradicting_evidence",
                   "confidence", "alternative_explanations", "unresolved_questions"),
    "experiment": ("experiment_id", "baseline_reference", "scratch_environment",
                   "exact_changes", "tool_invocation", "configuration", "execution_status",
                   "reproducibility", "estimated_cost"),
    "outcome": ("state", "summary", "metrics", "details"),
    "applicability": ("scope", "conditions", "validated_characteristics", "limitations",
                      "exclusions", "compatible_environments", "cross_design_reuse"),
    "evidence": ("observations", "hypotheses", "inferences", "experimentally_supported",
                 "validated_knowledge", "checksums", "before_after", "reviewer_findings"),
    "relationships": ("related_ids", "duplicate_of", "supersedes", "remedy_family"),
    "provenance": ("fde_records", "source_hashes", "record_source", "notes",
                   "captured_at", "capture_source"),
}
ALLOWED_REMEDY = ("remedy_id", "remedy_family", "description", "exact_modifications",
                  "preconditions", "compatibility", "expected_outcome", "risks",
                  "side_effects", "outcome")
REQUIRED_SUB = {
    "identity": ("investigation_id", "design_id", "design_fingerprint", "source_run"),
    "failure": ("category", "signature", "violation_type", "tool", "technology"),
    "root_cause": ("status", "hypothesis"),
    "experiment": ("experiment_id", "execution_status"),
    "outcome": ("state",),
    "applicability": ("scope", "conditions", "exclusions"),
    "evidence": ("observations", "inferences", "experimentally_supported",
                 "validated_knowledge", "checksums", "reviewer_findings"),
    "relationships": ("related_ids", "remedy_family"),
    "provenance": ("fde_records", "source_hashes"),
}

# Paths that the KB must never write to (relative to the project root).
PROTECTED_REL = (
    "benchmark", "runs", "experiments", "tools", "configs",
    "state/approval_policy.json", "state/approval_ledger.jsonl",
    "scripts/sattva_approval.py", "scripts/run_baseline_orfs.sh",
    "AGENTS.md",
)

STRONG_THRESHOLD = 0.70
PARTIAL_THRESHOLD = 0.40
COMPARABLE_SIGNATURE = 0.45
MIN_FAILURE_SIMILARITY = 0.15

STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are",
    "was", "were", "be", "by", "with", "at", "from", "as", "no", "not", "net",
    "design", "case", "run", "error", "warning", "stage", "tool", "result",
}


class KBError(Exception):
    """Raised for any rejected KB operation or unsafe path."""


# ---------------------------------------------------------------------------
# primitives
# ---------------------------------------------------------------------------
def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def atomic_write_json(path: Path, doc) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise KBError(f"invalid JSON at {path}: {exc}") from exc


def tokens(text) -> set[str]:
    if not isinstance(text, str):
        text = " ".join(str(x) for x in (text or [])) if isinstance(text, (list, tuple)) else str(text or "")
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS and len(t) > 1}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def contains_ratio(a: set[str], b: set[str]) -> float:
    """How much of b is covered by a (asymmetric, for query -> record)."""
    if not b:
        return 0.0
    return len(a & b) / len(b)


def as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


# ---------------------------------------------------------------------------
# safety boundary
# ---------------------------------------------------------------------------
def assert_safe_write(path: Path, knowledge_root: Path) -> None:
    """Refuse traversal, symlinks and any write outside the KB directory tree."""
    if ".." in path.parts:
        raise KBError(f"path traversal refused: {path}")
    for parent in (path.parent, *path.parent.parents):
        if parent.is_symlink():
            raise KBError(f"symlink component refused: {parent}")
    if path.is_symlink():
        raise KBError(f"target itself is a symlink: {path}")
    target = path.resolve()
    root = knowledge_root.resolve()
    if target != root and root not in target.parents:
        raise KBError(f"KB write outside knowledge root refused: {path}")


def protected_hashes(project_root: Path) -> dict[str, str]:
    """Hash the small, critical protected artifacts for immutability checks."""
    rels = [
        "AGENTS.md", "state/approval_policy.json",
        "scripts/sattva_approval.py", "scripts/run_baseline_orfs.sh",
        "benchmark/design/sattva_sram/config.mk",
        "benchmark/design/sattva_sram/constraint.sdc",
        "benchmark/design/sattva_sram/macro/sram_x4x4x1.lef",
        "benchmark/design/sattva_sram/macro/sram_x4x4x1.lib",
        "benchmark/design/sattva_sram/macro/sram_x4x4x1.gds",
    ]
    out = {}
    for rel in rels:
        p = project_root / rel
        if p.is_file():
            out[rel] = sha256_file(p)
        else:
            out[rel] = "MISSING"
    return out


def check_immutable(manifest: Path, project_root: Path) -> dict:
    doc = load_json(manifest)
    expected = doc.get("protected_hashes", {})
    results = {}
    for rel, want in expected.items():
        p = project_root / rel
        got = sha256_file(p) if p.is_file() else "MISSING"
        results[rel] = "OK" if got == want else "CHANGED"
    changed = [k for k, v in results.items() if v != "OK"]
    return {"status": "PASS" if not changed else "FAIL", "changed": changed,
            "results": results, "captured_at": doc.get("captured_at")}


# ---------------------------------------------------------------------------
# record validation / integrity
# ---------------------------------------------------------------------------
def record_digest(record: dict) -> str:
    payload = {k: v for k, v in record.items() if k != "integrity"}
    return sha256_bytes(canonical(payload).encode("utf-8"))


def validate_record(record: dict, *, require_evidence_for_pass: bool = True) -> None:
    if not isinstance(record, dict):
        raise KBError("record must be a JSON object")
    missing = [k for k in REQUIRED_TOP if k not in record]
    if missing:
        raise KBError(f"record missing required fields: {missing}")
    unknown_top = [k for k in record if k not in ALLOWED_TOP]
    if unknown_top:
        raise KBError(f"unknown record fields: {unknown_top}")
    version = record["record_version"]
    if not isinstance(version, int) or version < 1:
        raise KBError("record_version must be a positive integer")
    for section, keys in REQUIRED_SUB.items():
        sub = record.get(section)
        if not isinstance(sub, dict):
            raise KBError(f"record section must be an object: {section}")
        sub_missing = [k for k in keys if k not in sub]
        if sub_missing:
            raise KBError(f"record section {section} missing: {sub_missing}")
        sub_unknown = [k for k in sub if k not in ALLOWED_SUB[section]]
        if sub_unknown:
            raise KBError(f"unknown fields in {section}: {sub_unknown}")
    if not isinstance(record["remedies"], list) or not record["remedies"]:
        raise KBError("remedies must be a non-empty list")
    for rem in record["remedies"]:
        if not isinstance(rem, dict) or "remedy_id" not in rem or "remedy_family" not in rem:
            raise KBError("each remedy must have remedy_id and remedy_family")
        rem_unknown = [k for k in rem if k not in ALLOWED_REMEDY]
        if rem_unknown:
            raise KBError(f"unknown remedy fields: {rem_unknown}")
    supersedes = record["relationships"].get("supersedes")
    if supersedes and version < 2:
        raise KBError("a correction with supersedes must have record_version >= 2")
    if version >= 2 and not supersedes:
        raise KBError("record_version >= 2 requires relationships.supersedes")
    state = record["outcome"]["state"]
    if state not in OUTCOMES:
        raise KBError(f"invalid outcome state: {state}")
    rc = record["root_cause"]["status"]
    if rc not in ROOT_CAUSE_STATUS:
        raise KBError(f"invalid root cause status: {rc}")
    scope = record["applicability"]["scope"]
    if scope not in SCOPES:
        raise KBError(f"invalid applicability scope: {scope}")
    maturity = record["maturity"]
    if not isinstance(maturity, int) or not MATURITY_MIN <= maturity <= MATURITY_MAX:
        raise KBError("maturity must be an integer 0..4")
    if not isinstance(record["relationships"]["related_ids"], list):
        raise KBError("relationships.related_ids must be a list")

    # Scratch isolation: an executed experiment must not claim a production
    # design path as its scratch environment.
    exp = record["experiment"]
    scratch = str(exp.get("scratch_environment", "")).replace("\\", "/").lower()
    forbidden = ("benchmark/", "runs/orfs_baseline", "/design/", "configs/")
    if any(p in scratch for p in forbidden):
        raise KBError("experiment scratch_environment must be isolated; production design/baseline paths are forbidden")

    # Core anti-fabrication rule: a PASS claim needs supporting evidence.
    if state == "PASS" and require_evidence_for_pass:
        ev = record["evidence"]
        supported = as_list(ev.get("experimentally_supported")) + as_list(ev.get("validated_knowledge"))
        checksums = ev.get("checksums") or {}
        reports = as_list(record["failure"].get("reports"))
        if not supported or not (checksums or reports):
            raise KBError("PASS requires experimentally_supported/validated_knowledge evidence AND checksums or reports")
    # Inconclusive / blocked / not-run can never be recorded as a validated PASS;
    # maturity > 2 is reserved for replicated or cross-design evidence.
    if state in ("FAIL", "INCONCLUSIVE", "BLOCKED", "NOT_RUN") and maturity >= 3:
        raise KBError("maturity >= 3 cannot be assigned to a failed or unvalidated outcome")
    if maturity == 4:
        if (record["applicability"].get("cross_design_reuse") != "validated" or
                not record["relationships"]["related_ids"]):
            raise KBError("maturity 4 requires validated cross-design reuse and related cross-design records")


def seal_record(record: dict) -> dict:
    out = dict(record)
    out.setdefault("record_version", 1)
    out.setdefault("created_at", utc_now())
    out["integrity"] = {"algorithm": "sha256", "schema_version": SCHEMA_VERSION,
                        "record_sha256": record_digest(out)}
    return out


# ---------------------------------------------------------------------------
# append-oriented store
# ---------------------------------------------------------------------------
def chain_step(prev: str, record_hash: str) -> str:
    return sha256_bytes(canonical({"prev": prev, "record": record_hash}).encode("utf-8"))


class KBStore:
    def __init__(self, path: Path, knowledge_root: Path):
        self.path = Path(path)
        self.root = Path(knowledge_root)
        self.chain_path = self.path.parent / "kb_chain.json"
        assert_safe_write(self.path, self.root)

    def load(self) -> list[dict]:
        if not self.path.exists():
            return []
        out = []
        for n, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except ValueError as exc:
                raise KBError(f"corrupt KB line {n}: {exc}") from exc
            if not isinstance(rec, dict):
                raise KBError(f"KB line {n} is not an object")
            out.append(rec)
        return out

    def ids(self) -> set[str]:
        return {r.get("knowledge_id") for r in self.load()}

    def append(self, record: dict, *, allow_duplicate: bool = False) -> dict:
        validate_record(record)
        sealed = seal_record(record)
        kid = sealed["knowledge_id"]
        if not allow_duplicate and kid in self.ids():
            raise KBError(f"knowledge_id already exists (append-only): {kid}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = canonical(sealed) + "\n"
        lock = TargetLock(self.path) if TargetLock else None
        if lock:
            lock.__enter__()
        try:
            # Re-check under lock.
            if not allow_duplicate and kid in self.ids():
                raise KBError(f"knowledge_id already exists (append-only): {kid}")
            # A supersedes / related id must reference a real prior record.
            known = self.ids()
            refs = [sealed["relationships"].get("supersedes")] + as_list(
                sealed["relationships"].get("related_ids"))
            for ref in refs:
                if ref and ref not in known:
                    raise KBError(f"relationship references unknown record: {ref}")
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(line)
                fh.flush()
                os.fsync(fh.fileno())
            self._append_chain(sealed["integrity"]["record_sha256"])
        finally:
            if lock:
                lock.__exit__(None, None, None)
        return sealed

    def _append_chain(self, record_hash: str) -> None:
        state = load_json(self.chain_path) if self.chain_path.exists() else {
            "count": 0, "chain_sha256": ""}
        state = {"count": state.get("count", 0) + 1,
                 "chain_sha256": chain_step(state.get("chain_sha256", ""), record_hash),
                 "schema_version": SCHEMA_VERSION, "updated_at": utc_now()}
        assert_safe_write(self.chain_path, self.root)
        atomic_write_json(self.chain_path, state)

    def init_chain(self) -> dict:
        """One-time chain initialisation for an existing ledger (migration only)."""
        if self.chain_path.exists():
            raise KBError("append chain already initialised")
        prev, count = "", 0
        for rec in self.load():
            prev = chain_step(prev, record_digest(rec))
            count += 1
        state = {"count": count, "chain_sha256": prev,
                 "schema_version": SCHEMA_VERSION, "updated_at": utc_now()}
        assert_safe_write(self.chain_path, self.root)
        atomic_write_json(self.chain_path, state)
        return state

    def verify(self) -> dict:
        records = self.load()
        problems = []
        seen = set()
        prev, count = "", 0
        for i, rec in enumerate(records, 1):
            kid = rec.get("knowledge_id")
            if kid in seen:
                problems.append(f"duplicate knowledge_id at line {i}: {kid}")
            seen.add(kid)
            integrity = rec.get("integrity") or {}
            digest = record_digest(rec)
            if integrity.get("record_sha256") != digest:
                problems.append(f"integrity mismatch at line {i}: {kid}")
            prev = chain_step(prev, digest)
            count += 1
            try:
                validate_record(rec)
            except KBError as exc:
                problems.append(f"invalid record at line {i}: {exc}")
        # Append-chain and derived-manifest checks detect out-of-band deletion,
        # reordering or rewriting of historical lines.
        if self.chain_path.exists():
            chain = load_json(self.chain_path)
            if chain.get("count") != count or chain.get("chain_sha256") != prev:
                problems.append("append chain mismatch: ledger was reordered, deleted or rewritten")
        else:
            problems.append("append chain missing: run the chain-init migration once")
        manifest_path = self.path.parent / "kb_manifest.json"
        if manifest_path.exists():
            manifest = load_json(manifest_path)
            if manifest.get("store_sha256") and self.path.exists():
                if manifest["store_sha256"] != sha256_file(self.path):
                    problems.append("store hash mismatch against derived manifest")
        return {"status": "PASS" if not problems else "FAIL", "records": len(records),
                "chain_records": count, "problems": problems}


# ---------------------------------------------------------------------------
# derived manifest
# ---------------------------------------------------------------------------
def metrics(store: KBStore) -> dict:
    records = store.load()
    by_outcome, by_family, by_scope = {}, {}, {}
    maturity = {str(i): 0 for i in range(MATURITY_MIN, MATURITY_MAX + 1)}
    families: dict[str, list[str]] = {}
    related = 0
    for r in records:
        by_outcome[r["outcome"]["state"]] = by_outcome.get(r["outcome"]["state"], 0) + 1
        scope = r["applicability"]["scope"]
        by_scope[scope] = by_scope.get(scope, 0) + 1
        maturity[str(r["maturity"])] += 1
        fam = r["relationships"]["remedy_family"]
        by_family[fam] = by_family.get(fam, 0) + 1
        families.setdefault(fam, []).append(r["knowledge_id"])
        if r["relationships"].get("related_ids"):
            related += 1
    imm = store.root / "kb_immutable_manifest.json"
    return {
        "schema_version": SCHEMA_VERSION,
        "immutable_manifest_sha256": sha256_file(imm) if imm.is_file() else "",
        "total_records": len(records),
        "by_outcome": by_outcome,
        "by_scope": by_scope,
        "by_remedy_family": by_family,
        "maturity_histogram": maturity,
        "reuse_linked_records": related,
        "repeated_families": {k: v for k, v in families.items() if len(v) > 1},
        "historical_baseline_available": False,
        "note": "No historical time/cost baseline exists; measurement is enabled from this point forward.",
    }


def refresh_manifest(store: KBStore, manifest: Path) -> dict:
    doc = metrics(store)
    doc["generated_at"] = utc_now()
    doc["store_sha256"] = sha256_file(store.path) if store.path.exists() else ""
    assert_safe_write(manifest, store.root)
    atomic_write_json(manifest, doc)
    return doc


# ---------------------------------------------------------------------------
# retrieval
# ---------------------------------------------------------------------------
def query_tokens(q: dict) -> dict:
    return {
        "signature": tokens(q.get("failure_signature", "")),
        "violation": tokens(q.get("violation_type", "")),
        "root_cause": tokens(q.get("root_cause_hypothesis", "")),
        "context": tokens(" ".join(q.get("context_terms", []))),
        "technology": str(q.get("technology", "")).lower(),
        "layers": {str(x).lower() for x in q.get("routing_layers", [])},
        "tool": str(q.get("tool", "")).lower(),
        "design_fingerprint": str(q.get("design_fingerprint", "")),
    }


def factor_scores(record: dict, qt: dict) -> dict:
    fr = record["failure"]
    sig = tokens(fr.get("signature", "")) | tokens(fr.get("violation_type", ""))
    violation = tokens(fr.get("violation_type", ""))
    rc = tokens(record["root_cause"].get("hypothesis", "")) | tokens(
        record["root_cause"].get("status", ""))
    # An exact violation-code match is the strongest single identifier.
    violation_bonus = 0.25 if (qt["violation"] and qt["violation"] == violation) else 0.0
    failure_sim = min(1.0,
        0.7 * contains_ratio(qt["signature"] | qt["violation"], sig) +
        0.3 * jaccard(qt["signature"] | qt["violation"], sig) + violation_bonus)
    root_sim = jaccard(qt["root_cause"], rc)

    tech = str(fr.get("technology", "")).lower()
    layers = {str(x).lower() for x in as_list(fr.get("routing_layers"))}
    tool = str(fr.get("tool", "")).lower()
    fps = {str(record["identity"].get("design_fingerprint", ""))}
    compat = 0.0
    compat += 0.35 if (qt["technology"] and qt["technology"] == tech) else 0.0
    compat += 0.25 if (qt["layers"] and qt["layers"] & layers) else (0.15 if not qt["layers"] and not layers else 0.0)
    compat += 0.15 if (qt["tool"] and qt["tool"] == tool) else 0.0
    compat += 0.25 if (qt["design_fingerprint"] and qt["design_fingerprint"] in fps) else (0.10 if qt["technology"] == tech else 0.0)

    ev = record["evidence"]
    evidence_items = (as_list(ev.get("observations")) + as_list(ev.get("inferences")) +
                      as_list(ev.get("experimentally_supported")) +
                      as_list(ev.get("validated_knowledge")) +
                      as_list(ev.get("reviewer_findings")))
    evidence_quality = min(1.0, len(evidence_items) / 6.0 +
                           (0.25 if ev.get("checksums") else 0.0))
    outcomes = [r.get("outcome", "") for r in record.get("remedies", [])]
    record_state = record["outcome"]["state"]
    success = 1.0 if "PASS" in outcomes else 0.0
    # Maturity of a FAILED record is negative evidence only: it must not add
    # positive validation confidence to a recommendation score.
    validation = (record["maturity"] / MATURITY_MAX) if success else 0.0
    negative_evidence = 0.0 if success else (record["maturity"] / MATURITY_MAX)
    failure_hist = 1.0 if ("FAIL" in outcomes or record_state == "FAIL") else 0.0
    risks = sum(len(as_list(r.get("risks"))) + len(as_list(r.get("side_effects")))
                for r in record.get("remedies", []))
    risk_level = min(1.0, risks / 6.0)

    cond_text = " ".join(as_list(record["applicability"].get("conditions")))
    applicability = contains_ratio(qt["context"], tokens(cond_text))

    weights = {
        "failure_similarity": 0.28, "root_cause_similarity": 0.16,
        "compatibility": 0.20, "evidence_quality": 0.10,
        "validation_history": 0.06, "success_history": 0.04,
        "applicability_conditions": 0.10, "experiment_cost": 0.06,
    }
    exp_cfg = str(record.get("experiment", {}).get("estimated_cost", "full_flow")).lower()
    cost_score = 0.7 if exp_cfg in ("diagnostic", "low") else 0.3
    raw = (
        weights["failure_similarity"] * failure_sim +
        weights["root_cause_similarity"] * root_sim +
        weights["compatibility"] * compat +
        weights["evidence_quality"] * evidence_quality +
        weights["validation_history"] * validation +
        weights["success_history"] * success +
        weights["applicability_conditions"] * applicability +
        weights["experiment_cost"] * cost_score -
        0.08 * risk_level - 0.04 * failure_hist
    )
    return {
        "failure_similarity": round(failure_sim, 3),
        "root_cause_similarity": round(root_sim, 3),
        "compatibility": round(compat, 3),
        "evidence_quality": round(evidence_quality, 3),
        "validation_history": round(validation, 3),
        "negative_evidence_strength": round(negative_evidence, 3),
        "success_history": success,
        "failure_history": failure_hist,
        "risk_level": round(risk_level, 3),
        "experiment_cost": cost_score,
        "applicability_conditions": round(applicability, 3),
        "weights": weights,
        "score": round(max(0.0, min(1.0, raw)), 4),
    }


def search(store: KBStore, q: dict, limit: int = 10) -> dict:
    qt = query_tokens(q)
    results = []
    for rec in store.load():
        factors = factor_scores(rec, qt)
        results.append({
            "knowledge_id": rec["knowledge_id"],
            "record_sha256": (rec.get("integrity") or {}).get("record_sha256"),
            "outcome": rec["outcome"]["state"],
            "remedy_family": rec["relationships"]["remedy_family"],
            "scope": rec["applicability"]["scope"],
            "maturity": rec["maturity"],
            "factors": factors,
            "explanation": explain(rec, qt, factors),
        })
    results.sort(key=lambda r: (-r["factors"]["score"], r["knowledge_id"]))
    return {"query": q, "total_matches": len(results),
            "results": results[:limit]}


def explain(rec: dict, qt: dict, factors: dict) -> str:
    fr = rec["failure"]
    bits = [f"{rec['knowledge_id']}: {fr.get('violation_type')} / {fr.get('signature')[:80]}"]
    for key in ("failure_similarity", "root_cause_similarity", "compatibility",
                "evidence_quality", "validation_history", "negative_evidence_strength",
                "success_history",
                "failure_history", "risk_level", "experiment_cost",
                "applicability_conditions", "score"):
        bits.append(f"{key}={factors[key]}")
    bits.append(f"outcome={rec['outcome']['state']}")
    bits.append(f"scope={rec['applicability']['scope']}")
    if factors["failure_history"]:
        bits.append("HAS_FAILURE_HISTORY")
    return "; ".join(bits)


# ---------------------------------------------------------------------------
# duplicate detection / experiment suppression
# ---------------------------------------------------------------------------
def modification_digest(text) -> str:
    return sha256_bytes(canonical(as_list(text)).encode("utf-8"))


def duplicate_check(record: dict, store: KBStore) -> dict:
    fam = record["relationships"]["remedy_family"]
    sig = tokens(record["failure"].get("signature", "")) | tokens(
        record["failure"].get("violation_type", ""))
    q_viol = str(record["failure"].get("violation_type", "")).strip().lower()
    fp = str(record["identity"].get("design_fingerprint", ""))
    mod = {modification_digest(r.get("exact_modifications", "")) for r in record["remedies"]}
    matches = []
    for prior in store.load():
        if prior["knowledge_id"] == record["knowledge_id"]:
            continue
        pfam = prior["relationships"]["remedy_family"]
        psig = tokens(prior["failure"].get("signature", "")) | tokens(
            prior["failure"].get("violation_type", ""))
        pfp = str(prior["identity"].get("design_fingerprint", ""))
        pmod = {modification_digest(r.get("exact_modifications", "")) for r in prior["remedies"]}
        p_viol = str(prior["failure"].get("violation_type", "")).strip().lower()
        sig_sim = jaccard(sig, psig)
        comparable = sig_sim >= COMPARABLE_SIGNATURE or (q_viol and q_viol == p_viol)
        same_fam = pfam == fam
        same_fp = bool(fp) and fp == pfp
        if comparable and same_fam and same_fp:
            if mod & pmod:
                kind = "exact_duplicate"
            else:
                kind = "parameter_variation"
            matches.append({
                "prior_id": prior["knowledge_id"],
                "kind": kind,
                "signature_similarity": round(sig_sim, 3),
                "prior_outcome": prior["outcome"]["state"],
                "family": pfam,
                "suppressed": prior["outcome"]["state"] == "FAIL" and not record.get("new_justification"),
            })
        elif comparable and pfam != fam:
            matches.append({
                "prior_id": prior["knowledge_id"], "kind": "related_family",
                "signature_similarity": round(sig_sim, 3),
                "prior_outcome": prior["outcome"]["state"], "family": pfam,
                "suppressed": False,
            })
    return {"family": fam, "matches": matches,
            "any_suppressed": any(m["suppressed"] for m in matches)}


# ---------------------------------------------------------------------------
# applicability decision engine
# ---------------------------------------------------------------------------
def is_recommendable(record: dict) -> bool:
    """Only a verified, actionable remedy may be recommended as a STRONG_MATCH.

    A PASS on a diagnostic/finding record is evidence about the investigation,
    not a validated physical remedy (Agent D finding).
    """
    if record["outcome"]["state"] != "PASS":
        return False
    if record["relationships"]["remedy_family"] in NON_REMEDY_FAMILIES:
        return False
    return any(r.get("outcome") == "PASS" for r in record.get("remedies", []))


def assess(store: KBStore, q: dict) -> dict:
    ranked = search(store, q, limit=5)["results"]
    if not ranked:
        return {"classification": "NO_RELEVANT_KNOWLEDGE",
                "reason": "Knowledge Base is empty.", "trace": []}
    best = ranked[0]
    if best["factors"]["score"] < PARTIAL_THRESHOLD:
        return {"classification": "NO_RELEVANT_KNOWLEDGE",
                "reason": f"Top score {best['factors']['score']} below {PARTIAL_THRESHOLD}.",
                "trace": [best["knowledge_id"]]}
    # A failure with no signature overlap is a new investigation even if the
    # surrounding technology looks familiar (similarity is never proof).
    if best["factors"]["failure_similarity"] < MIN_FAILURE_SIMILARITY:
        return {"classification": "NO_RELEVANT_KNOWLEDGE",
                "reason": "No failure-signature overlap with any historical case.",
                "trace": [best["knowledge_id"]]}

    records = {r["knowledge_id"]: r for r in store.load()}
    top = records[best["knowledge_id"]]
    qt = query_tokens(q)

    # Hard exclusions are checked before any recommendation.
    exclusions = as_list(top["applicability"].get("exclusions"))
    ex_tokens = tokens(" ".join(exclusions))
    if ex_tokens and (qt["signature"] | qt["context"]) & ex_tokens:
        return {"classification": "INCOMPATIBLE",
                "reason": "Current context matches documented exclusion(s).",
                "exclusions": exclusions, "trace": [best["knowledge_id"]]}

    # Unvalidated / insufficient evidence cannot produce a recommendation.
    if best["factors"]["evidence_quality"] < 0.35 or top["outcome"]["state"] == "NOT_RUN":
        return {"classification": "INSUFFICIENT_EVIDENCE",
                "reason": "Insufficient evidence quality or NOT_RUN outcome.",
                "trace": [best["knowledge_id"]]}

    # Remedy-family failure suppression takes precedence over score. The
    # declared family (if any) is evaluated across ALL records, so a failed
    # family cannot escape suppression merely because a diagnostic ranks higher.
    probe_family = q.get("remedy_family") or top["relationships"]["remedy_family"]
    probe_identity = dict(top["identity"])
    probe_identity["design_fingerprint"] = q.get("design_fingerprint", probe_identity.get("design_fingerprint", ""))
    probe = {
        "knowledge_id": "PROBE", "record_version": SCHEMA_VERSION,
        "identity": probe_identity,
        "failure": dict(top["failure"], signature=q.get("failure_signature", ""),
                        violation_type=q.get("violation_type", "")),
        "remedies": [{"remedy_id": "PROBE", "remedy_family": probe_family,
                      "exact_modifications": q.get("exact_modifications", "")}],
        "relationships": dict(top["relationships"], remedy_family=probe_family),
    }
    dup = duplicate_check(probe, store)
    failed = [m for m in dup["matches"]
              if m["kind"] in ("exact_duplicate", "parameter_variation")
              and m["prior_outcome"] == "FAIL"]
    if failed:
        justification = str(q.get("new_justification", "")).strip()
        evidence_refs = as_list(q.get("new_evidence_refs"))
        if not justification or not evidence_refs:
            return {"classification": "PREVIOUSLY_FAILED",
                    "reason": "Same remedy family failed under comparable conditions; no new justification with evidence references supplied.",
                    "prior_records": failed,
                    "distinct_families": len({m["family"] for m in failed}),
                    "trace": [m["prior_id"] for m in failed]}
        # New evidence permits reconsideration only as PARTIAL (controlled validation).
        return {"classification": "PARTIAL_MATCH",
                "reason": "New justification with evidence references supplied; retry permitted only as controlled validation, not as validated remedy.",
                "prior_records": failed, "new_evidence_refs": evidence_refs,
                "distinct_families": len({m["family"] for m in failed}),
                "trace": [m["prior_id"] for m in failed],
                "required_validation": as_list(q.get("required_validation", []))}

    # Design-specific knowledge is never blindly generalized to another design.
    top_scope = top["applicability"]["scope"]
    top_fp = str(top["identity"].get("design_fingerprint", ""))
    q_fp = str(q.get("design_fingerprint", ""))
    if top_scope == "DESIGN_SPECIFIC" and (not q_fp or q_fp != top_fp):
        return {"classification": "PARTIAL_MATCH",
                "reason": "Design-specific evidence; cross-design promotion requires new validation.",
                "best_candidate": best["knowledge_id"],
                "trace": [best["knowledge_id"]],
                "required_validation": as_list(q.get("required_validation", [])) or
                                       ["validate in target design before reuse"]}

    if not is_recommendable(top):
        return {"classification": "PARTIAL_MATCH",
                "reason": "Best match is a finding/diagnostic record, not a validated actionable remedy; targeted evidence required.",
                "best_candidate": best["knowledge_id"],
                "trace": [best["knowledge_id"]]}

    if best["factors"]["score"] >= STRONG_THRESHOLD:
        risks = []
        for rem in top["remedies"]:
            risks.extend(as_list(rem.get("risks")))
            risks.extend(as_list(rem.get("side_effects")))
        return {"classification": "STRONG_MATCH",
                "reason": "High multi-factor score with a verified, actionable PASS precedent and no exclusions.",
                "recommendation": {
                    "knowledge_id": top["knowledge_id"],
                    "record_sha256": best["record_sha256"],
                    "remedy_family": top["relationships"]["remedy_family"],
                    "limitations": as_list(top["applicability"].get("limitations")),
                    "risks": risks,
                    "required_validation": as_list(q.get("required_validation", [])) or
                                           ["controlled validation in isolated scratch environment"],
                },
                "trace": [best["knowledge_id"]]}

    return {"classification": "PARTIAL_MATCH",
            "reason": "Some conditions match; targeted diagnostics required before an experiment.",
            "best_candidate": best["knowledge_id"],
            "missing_evidence": [k for k, v in best["factors"].items()
                                 if isinstance(v, (int, float)) and v < 0.4 and k != "score"],
            "trace": [best["knowledge_id"]]}


# ---------------------------------------------------------------------------
# FDE capture (FDE remains authoritative history; KB references it)
# ---------------------------------------------------------------------------
def capture_fde(store: KBStore, seed_file: Path, fde_root: Path) -> dict:
    doc = load_json(seed_file)
    records = doc.get("records")
    if not isinstance(records, list):
        raise KBError("seed file must contain a 'records' list")
    added, skipped = [], []
    for raw in records:
        kid = raw["knowledge_id"]
        if kid in store.ids():
            skipped.append(kid)
            continue
        prov = raw.setdefault("provenance", {})
        hashes = dict(prov.get("source_hashes") or {})
        for rel in as_list(prov.get("fde_records")):
            p = fde_root / rel
            if p.is_file():
                hashes[rel] = sha256_file(p)
            else:
                hashes[rel] = "MISSING"
        prov["source_hashes"] = hashes
        prov["captured_at"] = utc_now()
        prov.setdefault("capture_source", str(seed_file))
        sealed = store.append(raw)
        added.append(sealed["knowledge_id"])
    return {"added": added, "skipped_existing": skipped}


def verify_provenance(store: KBStore, fde_root: Path) -> dict:
    """Re-hash every captured FDE source; report drift without changing records."""
    rows = []
    for rec in store.load():
        prov = rec.get("provenance") or {}
        for rel, want in (prov.get("source_hashes") or {}).items():
            p = fde_root / rel
            got = sha256_file(p) if p.is_file() else "MISSING"
            rows.append({"knowledge_id": rec["knowledge_id"], "source": rel,
                         "captured": want[:16], "current": got[:16],
                         "status": "OK" if got == want else "CHANGED"})
    changed = [r for r in rows if r["status"] != "OK"]
    return {"status": "PASS" if not changed else "DRIFT",
            "checked": len(rows), "changed_count": len(changed),
            "changed_sources": sorted({r["source"] for r in changed}),
            "note": "FDE reports remain authoritative; drift is reported, never silent-rewritten.",
            "details": changed}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    i = sub.add_parser("init")
    i.add_argument("--knowledge-root", required=True)
    i.add_argument("--project-root", required=True)
    i.set_defaults(func=cmd_init)

    a = sub.add_parser("add")
    a.add_argument("--store", required=True)
    a.add_argument("--knowledge-root", required=True)
    a.add_argument("--record", required=True)
    a.set_defaults(func=cmd_add)

    s = sub.add_parser("seed")
    s.add_argument("--store", required=True)
    s.add_argument("--knowledge-root", required=True)
    s.add_argument("--seed-file", required=True)
    s.add_argument("--fde-root", required=True)
    s.set_defaults(func=cmd_seed)

    sr = sub.add_parser("search")
    sr.add_argument("--store", required=True)
    sr.add_argument("--knowledge-root", required=True)
    sr.add_argument("--query", required=True)
    sr.add_argument("--limit", type=int, default=10)
    sr.set_defaults(func=cmd_search)

    asr = sub.add_parser("assess")
    asr.add_argument("--store", required=True)
    asr.add_argument("--knowledge-root", required=True)
    asr.add_argument("--query", required=True)
    asr.set_defaults(func=cmd_assess)

    d = sub.add_parser("duplicates")
    d.add_argument("--store", required=True)
    d.add_argument("--knowledge-root", required=True)
    d.add_argument("--record", required=True)
    d.set_defaults(func=cmd_duplicates)

    v = sub.add_parser("verify")
    v.add_argument("--store", required=True)
    v.add_argument("--knowledge-root", required=True)
    v.set_defaults(func=cmd_verify)

    vi = sub.add_parser("verify-immutable")
    vi.add_argument("--manifest", required=True)
    vi.add_argument("--project-root", required=True)
    vi.set_defaults(func=cmd_verify_immutable)

    vp = sub.add_parser("verify-provenance")
    vp.add_argument("--store", required=True)
    vp.add_argument("--knowledge-root", required=True)
    vp.add_argument("--fde-root", required=True)
    vp.set_defaults(func=cmd_verify_provenance)

    ci = sub.add_parser("chain-init")
    ci.add_argument("--store", required=True)
    ci.add_argument("--knowledge-root", required=True)
    ci.set_defaults(func=cmd_chain_init)

    m = sub.add_parser("metrics")
    m.add_argument("--store", required=True)
    m.add_argument("--knowledge-root", required=True)
    m.set_defaults(func=cmd_metrics)
    return p


def _store(args) -> KBStore:
    return KBStore(Path(args.store), Path(args.knowledge_root))


def _out(doc) -> None:
    print(canonical(doc))


def cmd_init(args) -> None:
    root = Path(args.knowledge_root)
    root.mkdir(parents=True, exist_ok=True)
    store = KBStore(root / "kb_records.jsonl", root)
    manifest = root / "kb_manifest.json"
    if store.path.exists() and store.path.stat().st_size > 0:
        raise KBError("refusing init: KB ledger already exists")
    if not store.path.exists():
        store.path.touch()
    imm = root / "kb_immutable_manifest.json"
    atomic_write_json(imm, {"schema_version": SCHEMA_VERSION,
                            "captured_at": utc_now(),
                            "protected_hashes": protected_hashes(Path(args.project_root))})
    refresh_manifest(store, manifest)
    _out({"status": "PASS", "knowledge_root": str(root),
          "immutable_manifest": str(imm),
          "protected_count": len(load_json(imm)["protected_hashes"])})


def cmd_add(args) -> None:
    store = _store(args)
    rec = load_json(Path(args.record))
    dup = duplicate_check(rec, store)
    sealed = store.append(rec)
    refresh_manifest(store, Path(args.knowledge_root) / "kb_manifest.json")
    _out({"status": "PASS", "knowledge_id": sealed["knowledge_id"],
          "record_sha256": sealed["integrity"]["record_sha256"],
          "duplicates": dup["matches"]})


def cmd_seed(args) -> None:
    store = _store(args)
    report = capture_fde(store, Path(args.seed_file), Path(args.fde_root))
    refresh_manifest(store, Path(args.knowledge_root) / "kb_manifest.json")
    _out({"status": "PASS", **report})


def cmd_search(args) -> None:
    _out(search(_store(args), load_json(Path(args.query)), args.limit))


def cmd_assess(args) -> None:
    _out(assess(_store(args), load_json(Path(args.query))))


def cmd_duplicates(args) -> None:
    _out(duplicate_check(load_json(Path(args.record)), _store(args)))


def cmd_verify(args) -> None:
    _out(_store(args).verify())


def cmd_verify_immutable(args) -> None:
    _out(check_immutable(Path(args.manifest), Path(args.project_root)))


def cmd_verify_provenance(args) -> None:
    _out(verify_provenance(_store(args), Path(args.fde_root)))


def cmd_chain_init(args) -> None:
    _out({"status": "PASS", "chain": _store(args).init_chain()})


def cmd_metrics(args) -> None:
    _out(metrics(_store(args)))


def main() -> int:
    args = build_parser().parse_args()
    try:
        # CLI writes are restricted to a directory named 'knowledge' unless a
        # test explicitly opts out (module-level API remains testable).
        if hasattr(args, "knowledge_root") and not os.environ.get("SATTVA_KB_TEST_ROOT"):
            root = Path(args.knowledge_root).resolve()
            if root.name != "knowledge":
                raise KBError(f"CLI knowledge root must be a directory named 'knowledge': {root}")
        args.func(args)
    except KBError as exc:
        print(f"KB_ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
