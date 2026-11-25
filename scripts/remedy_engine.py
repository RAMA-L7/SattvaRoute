#!/usr/bin/env python3
"""Remedy-first engineering workflow engine (controller, no EDA).

Standard library only. Implements the decision layer:

    FAILURE -> DIAGNOSIS -> KB + WEB RESEARCH -> REMEDY RANKING
            -> CANDIDATE SELECTION -> SANDBOX TEST -> VALIDATION
            -> REPORT + KB

It never runs EDA, edits design inputs, or declares physical correctness.
Execution is delegated to an explicitly authorized harness. Timeouts and
unverified PASS results are neutralised to unresolved states.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Iterable

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUDGETS = ROOT / "config" / "remedy_budgets.json"

STAGES = ("FAILURE", "DIAGNOSIS", "RESEARCH", "RANK", "SELECT",
          "SANDBOX", "VALIDATE", "REPORT", "UNRESOLVED", "STOPPED")

EVIDENCE_SCORES = {
    "DIRECT_FIX": 1.0, "DOCUMENTED_FIX": 0.9, "SOURCE_VERIFIED": 0.85,
    "PAPER": 0.6, "DIRECT_EXPERIENCE": 0.6, "ANECDOTE": 0.4,
    "INFERENCE": 0.2, "UNKNOWN": 0.0,
}
APPLICABILITY_SCORES = {"EXACT": 1.0, "HIGH": 0.8, "PARTIAL": 0.5,
                        "INCOMPATIBLE": 0.0, "UNKNOWN": 0.0}
REVERSIBILITY_SCORES = {"FULL": 1.0, "PARTIAL": 0.5, "NONE": 0.0}
LEGALITY_STATES = {"PASS", "CONDITIONAL", "FAIL", "UNKNOWN"}
VALID_STATES = {"NOT_RUN", "RUNNING", "PASS", "FAIL", "INCONCLUSIVE", "TIMEOUT"}
REFUTED_OUTCOMES = {"FAIL", "BLOCKED", "REJECTED", "REFUTED"}
LEGALITY_BLOCK_REASONS = {"physical legality failed", "legality unverified"}
VALID_TRANSITIONS = {
    "FAILURE": {"DIAGNOSIS"},
    "DIAGNOSIS": {"RESEARCH"},
    "RESEARCH": {"RANK"},
    "RANK": {"SELECT"},
    "SELECT": {"SANDBOX", "REPORT"},
    "SANDBOX": {"VALIDATE", "REPORT"},
    "VALIDATE": {"REPORT"},
    "REPORT": set(),
    "UNRESOLVED": set(),
    "STOPPED": set(),
}
TERMINAL_STATES = {"FIX_VERIFIED", "CANDIDATES_EXHAUSTED", "RISK_EXCEEDS_POLICY",
                   "UNVERIFIED_PASS", "TIME_BUDGET_EXPIRED",
                   "BASELINE_INTEGRITY_FAIL", "UNAUTHORIZED_EXECUTION_REQUESTED"}
FAMILY_ALIASES = {
    "M4_OBS_CORRIDOR": "HAND_OBS_CARVE",
    "NARROW_CARVE": "HAND_OBS_CARVE",
    "MINIMAL_WEST_STRIP": "HAND_OBS_CARVE",
    "R1_N": "HAND_OBS_CARVE",
    "R1_N_W": "HAND_OBS_CARVE",
    "Y_CORRIDOR": "Y_ENVELOPE",
    "C1": "Y_ENVELOPE",
    "C2": "Y_ENVELOPE",
    "VIA_IN_PIN": "CONFIG_FLAG",
    "THRESHOLD_FLAG": "CONFIG_FLAG",
    "OBS_SPACING": "OBS_SPACING_SEMANTICS",
    "USEMINSPACING": "OBS_SPACING_SEMANTICS",
}


class WorkflowError(Exception):
    """Raised on an unsafe or inconsistent workflow transition."""


def normalize_family(family: str) -> str:
    return FAMILY_ALIASES.get(str(family), str(family))


def load_budgets(path: str | Path = DEFAULT_BUDGETS) -> dict[str, Any]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    required = ("budgets_minutes", "weights", "stop_conditions",
                "selection_min_score", "max_candidates_per_cycle")
    missing = [k for k in required if k not in data]
    if missing:
        raise WorkflowError(f"budget policy missing keys: {missing}")
    w = data["weights"]
    if abs(sum(w.values()) - 1.0) > 1e-9:
        raise WorkflowError("ranking weights must sum to 1.0")
    for key in ("stop_conditions",):
        if not isinstance(data[key], list) or not data[key]:
            raise WorkflowError(f"empty or invalid {key}")
    return data


@dataclass
class Candidate:
    candidate_id: str
    family: str
    mechanism: str
    evidence_strength: str = "UNKNOWN"
    applicability: str = "UNKNOWN"
    effectiveness: float = 0.0
    risk: float = 1.0
    cost_minutes: float = 60.0
    reversibility: str = "NONE"
    sources: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    legality: str = "UNKNOWN"
    predicted_outcome: str = ""
    refuted: bool = False
    notes: str = ""

    def validate(self) -> None:
        if self.evidence_strength not in EVIDENCE_SCORES:
            raise WorkflowError(f"unknown evidence strength: {self.evidence_strength}")
        if self.applicability not in APPLICABILITY_SCORES:
            raise WorkflowError(f"unknown applicability: {self.applicability}")
        if self.reversibility not in REVERSIBILITY_SCORES:
            raise WorkflowError(f"unknown reversibility: {self.reversibility}")
        if self.legality not in LEGALITY_STATES:
            raise WorkflowError(f"unknown legality: {self.legality}")
        for name in ("effectiveness", "risk"):
            if not 0.0 <= getattr(self, name) <= 1.0:
                raise WorkflowError(f"{name} must be within [0,1]")
        if self.cost_minutes < 0:
            raise WorkflowError("cost_minutes must be non-negative")


@dataclass
class RankedCandidate:
    candidate_id: str
    family: str
    score: float
    components: dict[str, float]
    eligible: bool
    reason: str


@dataclass
class BudgetTracker:
    """Monotonic budgets with independent per-stage and total accounting."""

    budgets: dict[str, Any]
    now_fn: Callable[[], float] = time.monotonic
    started_at: float = field(init=False)
    stage_starts: dict[str, float] = field(default_factory=dict)
    checkpoints: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.started_at = self.now_fn()

    def budget(self, stage: str) -> float:
        return float(self.budgets["budgets_minutes"].get(stage, 0)) * 60.0

    def enter_stage(self, stage: str) -> None:
        """Start a stage clock at stage entry, independent of total elapsed."""
        self.stage_starts[stage] = self.now_fn()

    def stage_elapsed(self, stage: str) -> float:
        start = self.stage_starts.get(stage)
        return max(0.0, self.now_fn() - start) if start is not None else 0.0

    def elapsed(self) -> float:
        """Total elapsed since controller construction."""
        return max(0.0, self.now_fn() - self.started_at)

    def checkpoint(self, stage: str, detail: str = "") -> dict[str, Any]:
        se, limit, te = self.stage_elapsed(stage), self.budget(stage), self.elapsed()
        cp = {"stage": stage, "stage_elapsed_s": round(se, 3),
              "total_elapsed_s": round(te, 3), "budget_s": limit,
              "remaining_s": round(limit - se, 3), "expired": limit > 0 and se > limit,
              "total_expired": te > self.budget("COMMON_ISSUE_TOTAL"),
              "detail": detail}
        self.checkpoints.append(cp)
        return cp

    def expired_stage(self, stage: str) -> bool:
        limit = self.budget(stage)
        return limit > 0 and self.stage_elapsed(stage) > limit

    def expired_total(self, kind: str = "COMMON_ISSUE_TOTAL") -> bool:
        return self.elapsed() > self.budget(kind)


def _component_breakdown(c: Candidate, budgets: dict[str, Any]) -> dict[str, float]:
    w = budgets["weights"]
    cap = max(1.0, float(budgets["budgets_minutes"].get("COMMON_ISSUE_TOTAL", 120)))
    return {
        "evidence": EVIDENCE_SCORES[c.evidence_strength] * w["evidence"],
        "applicability": APPLICABILITY_SCORES[c.applicability] * w["applicability"],
        "effectiveness": c.effectiveness * w["effectiveness"],
        "risk": (1.0 - c.risk) * w["risk"],
        "cost": max(0.0, 1.0 - c.cost_minutes / cap) * w["cost"],
        "reversibility": REVERSIBILITY_SCORES[c.reversibility] * w["reversibility"],
    }


def rank_candidates(candidates: Iterable[Candidate],
                    refuted_families: Iterable[str],
                    budgets: dict[str, Any]) -> list[RankedCandidate]:
    """Deterministic ranking with automatic refutation-family elimination."""
    refuted = {normalize_family(f) for f in refuted_families}
    out: list[RankedCandidate] = []
    for c in candidates:
        c.validate()
        comps = _component_breakdown(c, budgets)
        score = round(sum(comps.values()), 6)
        fam = normalize_family(c.family)
        reason, eligible = "eligible", True
        if c.refuted or fam in refuted:
            eligible, reason = False, "previously refuted"
        elif c.applicability == "INCOMPATIBLE":
            eligible, reason = False, "applicability incompatible"
        elif c.legality == "FAIL":
            eligible, reason = False, "physical legality failed"
        elif c.legality == "UNKNOWN":
            eligible, reason = False, "legality unverified"
        elif c.evidence_strength == "UNKNOWN" and c.applicability != "EXACT":
            eligible, reason = False, "insufficient evidence"
        out.append(RankedCandidate(c.candidate_id, fam, score, comps, eligible, reason))
    out.sort(key=lambda r: (-r.score, r.candidate_id))
    return out


def kb_refuted_families(kb_records_path: str | Path,
                        signature_hint: str = "") -> list[str]:
    """Extract refuted families from the existing KB ledger (read-only)."""
    path = Path(kb_records_path)
    if not path.exists():
        return []
    families: set[str] = set()
    tokens = [t.lower() for t in signature_hint.split() if len(t) > 3]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        sig = str(rec.get("failure", {}).get("signature", "")).lower()
        if tokens and not any(t in sig for t in tokens):
            continue
        for remedy in rec.get("remedies", []):
            outcome = str(remedy.get("outcome", "")).upper()
            fam = normalize_family(remedy.get("remedy_family", ""))
            desc = str(remedy.get("description", ""))
            obs = " ".join(str(x) for x in
                           rec.get("evidence", {}).get("observations", [])).lower()
            if outcome in REFUTED_OUTCOMES or any(
                    k in obs for k in ("refut", "rejected", "no ap", "0 ap")):
                if fam:
                    families.add(fam)
                elif desc:
                    families.add(desc[:80])
    return sorted(families)


@dataclass
class WorkflowResult:
    failure_id: str
    stages: list[str] = field(default_factory=lambda: ["FAILURE"])
    selection: str | None = None
    ranked: list[RankedCandidate] = field(default_factory=list)
    stop_condition: str = "CANDIDATES_EXHAUSTED"
    unresolved_gap: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
    checkpoints: list[dict[str, Any]] = field(default_factory=list)
    execution_state: str = "NOT_RUN"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RemedyEngine:
    """Decision-layer controller for one failure case."""

    def __init__(self, failure_id: str, budgets: dict[str, Any] | None = None,
                 now_fn: Callable[[], float] = time.monotonic,
                 execute: Callable[[Candidate], dict[str, Any]] | None = None,
                 authorized: bool = False):
        self.failure_id = failure_id
        self.budgets = budgets or load_budgets()
        self.budget = BudgetTracker(self.budgets, now_fn=now_fn)
        self.execute = execute
        self.authorized = authorized  # deprecated shim; prefer approval binding
        self.approval: dict[str, Any] | None = None
        self.state_path: Path | None = None
        self.cancel_event: Any = None  # set by caller; harness must poll it
        self.result = WorkflowResult(failure_id=failure_id)
        self._candidates: list[Candidate] = []
        self._attempted: set[str] = set()
        self._terminal = False
        self._diagnosed = False
        self._last_stage = "FAILURE"

    def _set_stop(self, condition: str, gap: str) -> None:
        if condition not in self.budgets["stop_conditions"]:
            raise WorkflowError(f"unknown stop condition: {condition}")
        self.result.stop_condition = condition
        self.result.unresolved_gap = gap
        self._terminal = True

    def _assert_active(self) -> None:
        if self._terminal:
            raise WorkflowError(
                f"workflow is terminal ({self.result.stop_condition}); no further transitions")

    def _stage(self, name: str, detail: str = "") -> None:
        if name not in STAGES:
            raise WorkflowError(f"unknown stage: {name}")
        if name not in ("REPORT", "UNRESOLVED", "STOPPED"):
            self._assert_active()
            allowed = VALID_TRANSITIONS.get(self._last_stage, set())
            if name not in allowed:
                raise WorkflowError(
                    f"invalid transition {self._last_stage} -> {name}; allowed={sorted(allowed)}")
        self.budget.enter_stage(name)
        cp = self.budget.checkpoint(name, detail)
        self.result.stages.append(name)
        self._last_stage = name
        if cp["expired"] and name not in ("SANDBOX", "VALIDATE"):
            self._set_stop("TIME_BUDGET_EXPIRED",
                           f"stage {name} exceeded its {self.budget.budget(name) / 60:g} min budget")

    def diagnose(self, diagnosis_evidence: dict[str, Any]) -> None:
        self._stage("DIAGNOSIS", "reused existing evidence")
        self._diagnosed = True
        self.result.evidence["diagnosis"] = diagnosis_evidence
        if not diagnosis_evidence.get("signature"):
            self._set_stop("CANDIDATES_EXHAUSTED", "missing failure signature")

    def research(self, candidates: list[Candidate], sources: dict[str, list[str]],
                 refuted_families: Iterable[str]) -> None:
        self._stage("RESEARCH", f"{len(candidates)} candidates")
        copied = []
        for c in candidates:
            c.validate()
            data = asdict(c)
            data["family"] = normalize_family(data["family"])
            data["sources"] = list(sources.get(c.candidate_id, c.sources))
            if not data["sources"] and data["evidence_strength"] != "INFERENCE":
                data["evidence_strength"] = "UNKNOWN"
            copied.append(Candidate(**data))
        self._candidates = copied
        self.result.evidence["refuted_families"] = sorted(
            {normalize_family(f) for f in refuted_families})

    def rank_and_select(self) -> Candidate | None:
        self._stage("RANK")
        self.result.ranked = rank_candidates(
            self._candidates, self.result.evidence["refuted_families"], self.budgets)
        self._stage("SELECT")
        eligible = [r for r in self.result.ranked
                    if r.eligible and r.candidate_id not in self._attempted
                    and r.score >= float(self.budgets["selection_min_score"])]
        eligible = eligible[:int(self.budgets["max_candidates_per_cycle"])]
        if not eligible:
            blocked = [r for r in self.result.ranked if r.reason in LEGALITY_BLOCK_REASONS]
            if blocked:
                c = next(x for x in self._candidates if x.candidate_id == blocked[0].candidate_id)
                pre = ", ".join(c.prerequisites) or "none recorded"
                self._set_stop("RISK_EXCEEDS_POLICY",
                               f"{c.candidate_id}: {blocked[0].reason}; prerequisites={pre}")
                self.result.evidence["gated_candidate"] = c.candidate_id
            else:
                self._set_stop("CANDIDATES_EXHAUSTED",
                               "no eligible candidate above threshold after refutation filtering")
            self.result.selection = None
            return None
        best = eligible[0]
        c = next(x for x in self._candidates if x.candidate_id == best.candidate_id)
        if c.legality != "PASS":
            pre = ", ".join(c.prerequisites) or "none recorded"
            self._set_stop("RISK_EXCEEDS_POLICY",
                           f"{c.candidate_id}: physical legality={c.legality}; prerequisites={pre}")
            self.result.evidence["gated_candidate"] = c.candidate_id
            self.result.selection = None
            return None
        self.result.selection = best.candidate_id
        return c

    def record_failure_and_advance(self, candidate_id: str, reason: str) -> Candidate | None:
        self._attempted.add(candidate_id)
        self.result.evidence.setdefault("attempts", []).append(
            {"candidate_id": candidate_id, "outcome": "FAIL", "reason": reason})
        self._last_stage = "RESEARCH"  # re-enter ranking for the next attempt
        return self.rank_and_select()

    def skip_execution(self, reason: str) -> None:
        """Explicitly record skipped SANDBOX/VALIDATE stages (no silent omission)."""
        if not self._diagnosed:
            raise WorkflowError("cannot skip execution before diagnosis")
        if self._terminal:
            # A gated stop still records explicitly why execution did not happen.
            for stage in ("SANDBOX", "VALIDATE"):
                self.budget.enter_stage(stage)
                self.result.stages.append(stage)
                self.result.checkpoints.append(self.budget.checkpoint(stage, "SKIPPED"))
            self._last_stage = "VALIDATE"
        else:
            self._stage("SANDBOX", "SKIPPED")
            self._stage("VALIDATE", "SKIPPED")
        self.result.execution_state = "NOT_RUN"
        self.result.evidence["execution"] = {"state": "NOT_RUN", "skipped": True,
                                             "reason": reason}

    def cancel(self, reason: str = "operator or timeout cancellation") -> None:
        """Request cancellation; the harness must poll the event and stop work."""
        if self.cancel_event is not None and hasattr(self.cancel_event, "set"):
            self.cancel_event.set()
        self.result.evidence.setdefault("cancellation", []).append(reason)
        if self.result.execution_state in ("RUNNING", "NOT_RUN"):
            self.result.execution_state = "TIMEOUT"
        self._set_stop("TIME_BUDGET_EXPIRED", reason)

    def save_state(self) -> dict[str, Any]:
        """Persist pre-execution state so interruption can be reconciled."""
        if self.state_path is None:
            return {"status": "SKIPPED", "reason": "no state_path configured"}
        snap = {"failure_id": self.failure_id, "stages": self.result.stages,
                "selection": self.result.selection,
                "attempted": sorted(self._attempted),
                "phase": "started" if self.result.execution_state == "RUNNING" else "idle",
                "stop_condition": self.result.stop_condition,
                "ledger_head": self.result.evidence.get("ledger_head")}
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n",
                                   encoding="utf-8")
        return {"status": "PASS", "path": str(self.state_path), "phase": snap["phase"]}

    def load_state(self, state_path: str | Path) -> dict[str, Any]:
        """Reconcile an interrupted state without implicitly re-running EDA."""
        p = Path(state_path)
        if not p.is_file():
            return {"status": "PASS", "state": None}
        state = json.loads(p.read_text(encoding="utf-8"))
        if state.get("phase") == "started":
            self._set_stop("BASELINE_INTEGRITY_FAIL",
                           "interrupted execution state requires operator reconciliation")
        else:
            self.result.stages = list(state.get("stages", []))
            self.result.selection = state.get("selection")
            self._attempted = set(state.get("attempted", []))
        return {"status": "PASS", "state": state}

    def _assert_can_execute(self, candidate: Candidate) -> None:
        self._assert_active()
        if not self._diagnosed:
            raise WorkflowError("execution before diagnosis is forbidden")
        if self.result.selection is None or candidate.candidate_id != self.result.selection:
            raise WorkflowError(
                f"candidate {candidate.candidate_id} is not the selected candidate "
                f"({self.result.selection})")
        if candidate.candidate_id in self._attempted:
            raise WorkflowError(
                f"candidate {candidate.candidate_id} already attempted; new attempt required")
        if self.budget.expired_total() or self.budget.expired_stage("SANDBOX"):
            self._set_stop("TIME_BUDGET_EXPIRED", "budget expired before execution")
            raise WorkflowError("execution blocked: time budget expired")
        if self.execute is not None and self.approval is None and not self.authorized:
            self._set_stop("UNAUTHORIZED_EXECUTION_REQUESTED",
                           "execution requires an approved operation or explicit legacy shim")
            raise WorkflowError("execution not authorized")

    def _verify_evidence(self, candidate: Candidate, outcome: dict[str, Any]) -> dict[str, Any]:
        """Evidence bar: callback flags alone never prove a verified recovery."""
        ev = outcome.get("evidence")
        if not isinstance(ev, dict):
            return {"verified": False, "reason": "missing evidence object"}
        required = ("artifacts", "metrics", "reviewer", "baseline_ref", "treatment_ref",
                    "checksums")
        missing = [k for k in required if not ev.get(k)]
        if missing:
            return {"verified": False, "reason": f"evidence missing: {missing}"}
        if outcome.get("state") != "PASS":
            return {"verified": False, "reason": "worker outcome is not PASS"}
        return {"verified": True, "reason": "artifacts, metrics, checksums and reviewer recorded"}

    def sandbox_and_validate(self, candidate: Candidate) -> dict[str, Any]:
        self._assert_can_execute(candidate)
        if self.execute is None:
            return self.skip_execution(
                "no approved execution harness supplied; engine never executes EDA implicitly")
        if self.approval is not None:
            from sattva_approval import ApprovalError, validate_approval
            policy = self.approval.get("policy")
            if policy is None:
                raise WorkflowError("approval binding requires a policy")
            try:
                check = validate_approval(
                    self.approval["record"], Path(self.approval["patch"]), Path(policy),
                    Path(self.approval["design_root"]),
                    run_id=self.approval["source_run_id"],
                    decision_id=self.approval.get("decision_id"))
            except (ApprovalError, KeyError, TypeError) as exc:
                self._set_stop("UNAUTHORIZED_EXECUTION_REQUESTED", f"approval binding failed: {exc}")
                raise WorkflowError(f"approval binding failed: {exc}") from exc
            self.result.evidence["approval"] = check
        self._stage("SANDBOX", candidate.candidate_id)
        self._attempted.add(candidate.candidate_id)
        self.result.execution_state = "RUNNING"
        self.save_state()
        outcome = self.execute(candidate)
        state = str(outcome.get("state", "INCONCLUSIVE"))
        if state not in VALID_STATES:
            raise WorkflowError("invalid execution state returned")
        self.result.execution_state = state
        self.result.evidence["execution"] = outcome
        self.save_state()
        if state == "TIMEOUT":
            self._set_stop("TIME_BUDGET_EXPIRED", "worker timeout; evidence preserved")
            return outcome
        if state == "PASS":
            verdict = self._verify_evidence(candidate, outcome)
            self.result.evidence["verification"] = verdict
            if verdict["verified"]:
                self._set_stop("FIX_VERIFIED",
                               f"{candidate.candidate_id}: {verdict['reason']}")
            else:
                self._set_stop("UNVERIFIED_PASS",
                               f"{candidate.candidate_id}: {verdict['reason']}")
        return outcome

    def report_kb(self, ledger: str | Path, record_id: str) -> dict[str, Any]:
        """Append the RUN outcome to the remedy KB sidecar (append-only, idempotent)."""
        from remedy_kb import append_record, load_records, verify
        path = Path(ledger)
        if verify(path)["status"] != "PASS":
            raise WorkflowError("remedy KB chain is invalid; refusing append")
        if any(r.get("record_id") == record_id for r in load_records(path)):
            return {"status": "PASS", "record_id": record_id, "appended": False}
        payload = {"failure_id": self.failure_id,
                   "stages": self.result.stages,
                   "selection": self.result.selection,
                   "stop_condition": self.result.stop_condition,
                   "unresolved_gap": self.result.unresolved_gap,
                   "execution_state": self.result.execution_state,
                   "evidence": self.result.evidence}
        sealed = append_record(path, {"record_id": record_id,
                                      "type": "engineering_conclusion",
                                      "created_at": __import__("remedy_kb").utc_now(),
                                      "payload": payload})
        return {"status": "PASS", "record_id": record_id, "appended": True,
                "record_hash": sealed["record_hash"]}

    def report(self) -> dict[str, Any]:
        """REPORT stage: separate execution outcome from reporting outcome.

        A measured PASS is never erased because report formatting exceeded a
        budget. The report instead flags the timing condition explicitly.
        """
        self._stage("REPORT", self.result.stop_condition)
        self.result.checkpoints = self.budget.checkpoints
        execution_outcome = self.result.execution_state
        if self.budget.expired_total() and not self._terminal:
            self._set_stop("TIME_BUDGET_EXPIRED",
                           "time budget expired before a verified fix; "
                           "see checkpoints for the stage that consumed it")
        if execution_outcome == "PASS" and self.result.stop_condition not in (
                "FIX_VERIFIED", "UNVERIFIED_PASS"):
            self._set_stop("UNVERIFIED_PASS", "PASS recorded without verified evidence")
        if self.budget.expired_total() and execution_outcome == "PASS":
            self.result.evidence["report_verdict"] = "EXPIRED_AFTER_MEASUREMENT"
            self.result.evidence["execution_outcome_preserved"] = execution_outcome
        if self.result.stop_condition == "CANDIDATES_EXHAUSTED" and not self.result.unresolved_gap:
            self.result.unresolved_gap = "no qualified candidate remained"
        out = self.result.to_dict()
        out["execution_outcome"] = execution_outcome
        out["report_outcome"] = self.result.stop_condition
        out["timing"] = {"total_elapsed_s": round(self.budget.elapsed(), 3),
                         "total_budget_s": self.budget.budget("COMMON_ISSUE_TOTAL"),
                         "expired": self.budget.expired_total()}
        return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("rank", help="rank candidates from a JSON file")
    r.add_argument("--candidates", required=True)
    r.add_argument("--kb-records", default=str(ROOT / "knowledge" / "kb_records.jsonl"))
    r.add_argument("--signature-hint", default="")
    r.add_argument("--budgets", default=str(DEFAULT_BUDGETS))
    r.set_defaults(func=lambda a: {
        "status": "PASS",
        "refuted_families": sorted(set(kb_refuted_families(a.kb_records, a.signature_hint))
                                   | set(json.loads(Path(a.candidates).read_text(
                                       encoding="utf-8")).get("refuted_families", []))),
        "ranked": [asdict(x) for x in rank_candidates(
            [Candidate(**c) for c in json.loads(
                Path(a.candidates).read_text(encoding="utf-8")).get("candidates", [])],
            kb_refuted_families(a.kb_records, a.signature_hint), load_budgets(a.budgets))]})
    return p


def _out(obj: Any) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True))


def main() -> int:
    args = build_parser().parse_args()
    _out(args.func(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
