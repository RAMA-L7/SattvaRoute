#!/usr/bin/env python3
"""Strict, report-level verification of a SattvaRoute ORFS run (offline).

This module separates five questions that a return code cannot answer:

  1. execution      -- did every declared stage run, in this run directory?
  2. artifacts      -- are the endpoint products present and non-empty?
  3. engineering    -- do the reports show clean routing/timing/extraction?
  4. evidence       -- is the evidence complete enough to support the claim?
  5. recovery       -- did an approved change actually fix the target failure?

Every check returns PASS / FAIL / UNKNOWN / NOT_EVALUATED. The rule that
matters most: *missing evidence is never a pass*. Two identically incomplete
runs both FAIL, and an empty report is only clean when the tool log shows the
run completed with a zero violation count.

Routing deliberately reads the LAST DRT-0199 count in the stage log. Detailed
routing prints intermediate counts (e.g. 25 -> 2 -> 0); taking the first match
is how a stale or partial run is misreported as dirty, and taking "no report
lines" as clean is how an incomplete run is misreported as clean.

Usage:
    python3 scripts/verify_run.py --run runs/<id> [--audit audit.json] [--json]
    python3 scripts/verify_run.py --baseline B --failure F --recovery R \
        --audit-map audits.json --approval-apply A.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

PASS, FAIL, UNKNOWN, NOT_EVALUATED = "PASS", "FAIL", "UNKNOWN", "NOT_EVALUATED"

# Endpoint products a completed control-benchmark run must contain.
ENDPOINT_ARTIFACTS = (
    "5_route.odb",
    "route.guide",
    "6_final.odb",
    "6_final.spef",
    "6_final.def",
    "6_final.gds",
    "6_final.v",
    "6_final.sdc",
)
ENDPOINT_REPORTS = ("6_finish.rpt", "5_route_drc.rpt")

DRT_COUNT_RE = re.compile(r"\[INFO DRT-0199\]\s+Number of violations\s*=\s*(\d+)")
RCX_RE = re.compile(r"\[INFO RCX-0045\]\s+Extract\s+(\d+)\s+nets")
UNANNOTATED_RE = re.compile(r"Found\s+(\d+)\s+unannotated drivers")
CLOCK_PERIOD_RE = re.compile(r"period_min\s*=\s*([0-9.]+|inf)\s*fmax\s*=\s*(\S+)")
WORST_SLACK_RE = re.compile(r"worst slack max\s+(-?[0-9.]+)")
SETUP_RE = re.compile(r"setup violation count\s+(\d+)")
HOLD_RE = re.compile(r"hold violation count\s+(\d+)")
TNS_RE = re.compile(r"tns max\s+(-?[0-9.]+)")
WNS_RE = re.compile(r"wns max\s+(-?[0-9.]+)")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


@dataclass
class Check:
    name: str
    status: str
    detail: str
    evidence: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "status": self.status,
                "detail": self.detail, "evidence": self.evidence}


@dataclass
class RunView:
    run_dir: Path
    run: dict[str, Any]
    evidence: Path
    work: Path

    @property
    def results(self) -> Path:
        return self.work / "results"

    @property
    def reports(self) -> Path:
        return self.work / "reports"

    def find(self, base: Path, name: str) -> list[Path]:
        return sorted(base.rglob(name)) if base.is_dir() else []


def load_run(run_dir: str | Path) -> RunView:
    run = Path(run_dir)
    evidence = run / "evidence"
    doc: dict[str, Any] = {}
    run_json = evidence / "run.json"
    if run_json.is_file():
        doc = json.loads(run_json.read_text(encoding="utf-8"))
    return RunView(run, doc, evidence, run / "work")


# --------------------------------------------------------------------------
# 1. execution
# --------------------------------------------------------------------------
def check_execution(view: RunView) -> Check:
    if not view.run:
        return Check("execution", FAIL, "evidence/run.json missing or unreadable",
                     [str(view.evidence / "run.json")])
    stages = view.run.get("stages") or []
    if not stages:
        return Check("execution", FAIL, "run.json declares no executed stages",
                     [str(view.evidence / "run.json")])
    missing_logs = [s["stage"] for s in stages
                    if not (view.evidence / f"stage_{s['stage']}.log").is_file()]
    rc = view.run.get("overall_rc")
    failed = [s for s in stages if int(s.get("rc", 1)) != 0]
    if missing_logs:
        return Check("execution", FAIL,
                     f"stage logs missing for {missing_logs}",
                     [str(view.evidence)])
    if rc != 0:
        return Check("execution", FAIL,
                     f"overall_rc={rc}; first_failed_stage="
                     f"{view.run.get('first_failed_stage')}",
                     [str(view.evidence / "run.json")])
    if failed:
        return Check("execution", FAIL,
                     f"non-zero stage rcs present: {failed}",
                     [str(view.evidence / "stages.tsv")])
    return Check("execution", PASS,
                 f"{len(stages)} stages rc=0; logs present",
                 [str(view.evidence / "run.json")])


# --------------------------------------------------------------------------
# 2. artifacts
# --------------------------------------------------------------------------
def check_artifacts(view: RunView) -> Check:
    found: dict[str, int] = {}
    missing: list[str] = []
    empty: list[str] = []
    for name in ENDPOINT_ARTIFACTS:
        hits = [p for p in view.find(view.results, name) if p.is_file()]
        if not hits:
            missing.append(name)
            continue
        found[name] = max(p.stat().st_size for p in hits)
        if found[name] == 0:
            empty.append(name)
    for name in ENDPOINT_REPORTS:
        hits = [p for p in view.find(view.reports, name) if p.is_file()]
        if not hits:
            missing.append(name)
        else:
            found[name] = max(p.stat().st_size for p in hits)

    evidence = [str(p) for p in view.results.rglob("*") if p.is_file()][:5]
    if missing:
        return Check("artifacts", FAIL,
                     f"missing endpoint artifacts: {sorted(missing)}; "
                     f"present={sorted(found)}", evidence)
    if empty:
        return Check("artifacts", FAIL, f"zero-byte endpoint artifacts: {empty}",
                     evidence)
    # A zero-byte DRC report is legitimate only when routing proves zero
    # violations; that correlation is enforced in check_routing().
    return Check("artifacts", PASS,
                 f"{len(found)} endpoint artifacts present and non-empty", evidence)


def check_stale_reports(view: RunView) -> Check:
    """Reports must post-date the start of the run that owns them."""
    stages = view.run.get("stages") or []
    if not stages:
        return Check("report_freshness", UNKNOWN, "no stage timestamps in run.json")
    try:
        start = datetime.fromisoformat(stages[0]["start"])
    except (KeyError, ValueError) as exc:
        return Check("report_freshness", UNKNOWN, f"unparseable run start: {exc}")
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    stale: list[str] = []
    seen = 0
    for name in ENDPOINT_REPORTS:
        for p in view.find(view.reports, name):
            seen += 1
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            if mtime < start:
                stale.append(f"{p.name} mtime {mtime.isoformat()} < run start "
                             f"{start.isoformat()}")
    if not seen:
        return Check("report_freshness", NOT_EVALUATED,
                     "no endpoint reports to date-check", [str(view.reports)])
    if stale:
        return Check("report_freshness", FAIL,
                     "reports older than the run that cites them: " + "; ".join(stale),
                     [str(view.reports)])
    return Check("report_freshness", PASS,
                 "all endpoint reports are newer than the run start",
                 [str(view.reports)])


# --------------------------------------------------------------------------
# 3. routing
# --------------------------------------------------------------------------
def check_routing(view: RunView) -> Check:
    log = view.evidence / "stage_route.log"
    if not log.is_file():
        return Check("routing", UNKNOWN, "stage_route.log missing", [str(log)])
    text = read_text(log)
    counts = [int(m.group(1)) for m in DRT_COUNT_RE.finditer(text)]
    if not counts:
        return Check("routing", UNKNOWN,
                     "no DRT-0199 violation summary in route log; "
                     "absence is not evidence of a clean route", [str(log)])
    final = counts[-1]
    completed = ("5_2_route.odb" in text) or ("fillcell.tcl" in text)
    reports = [p for p in view.find(view.reports, "5_route_drc.rpt") if p.is_file()]
    report_bytes = sum(p.stat().st_size for p in reports)
    detail = (f"DRT-0199 sequence {counts}; final={final}; "
              f"route_completion_marker={completed}; drc_report_bytes={report_bytes}")
    if not completed:
        return Check("routing", FAIL,
                     detail + "; detailed routing did not reach its write/exit step",
                     [str(log)])
    if final != 0:
        return Check("routing", FAIL, detail + "; final violations nonzero",
                     [str(log)])
    if report_bytes:
        return Check("routing", FAIL,
                     detail + "; non-empty DRC report contradicts zero count",
                     [str(p) for p in reports])
    return Check("routing", PASS,
                 detail + "; empty DRC report corroborated by final count 0", [str(log)])


# --------------------------------------------------------------------------
# 4. timing
# --------------------------------------------------------------------------
def check_timing(view: RunView, audit: dict[str, Any] | None) -> Check:
    report = view.find(view.reports, "6_finish.rpt")
    if not report:
        return Check("timing", UNKNOWN, "6_finish.rpt missing")
    text = read_text(report[0])
    setup = SETUP_RE.search(text)
    hold = HOLD_RE.search(text)
    worst = WORST_SLACK_RE.search(text)
    period = CLOCK_PERIOD_RE.search(text)
    if not (setup and hold and worst and period):
        return Check("timing", UNKNOWN,
                     "6_finish.rpt lacks one of setup/hold/worst-slack/period_min; "
                     "unrecognized format is not zero violations",
                     [str(report[0])])
    if audit is None:
        return Check("timing", UNKNOWN,
                     "no timing-unit audit supplied; numeric values cannot be "
                     "attributed to a unit or corner", [str(report[0])])
    units = audit.get("units") or {}
    if not units.get("time"):
        return Check("timing", UNKNOWN,
                     "timing audit has no time unit; refusing to interpret numbers",
                     [str(report[0])])
    clock_period_file = view.find(view.results, "clock_period.txt")
    declared = None
    if clock_period_file:
        try:
            declared = float(read_text(clock_period_file[0]).strip())
        except ValueError:
            declared = None
    executed = (audit.get("clock") or {}).get("period")
    detail = (f"units={units.get('time')}; clock_period.txt={declared}; "
              f"audit_clock_period={executed}; worst_slack={worst.group(1)}; "
              f"period_min={period.group(1)} fmax={period.group(2)}; "
              f"setup={setup.group(1)} hold={hold.group(1)}")
    if declared is not None and executed is not None and abs(declared - float(executed)) > 1e-9:
        return Check("timing", FAIL,
                     detail + "; executed clock differs from recorded clock period",
                     [str(report[0])])
    if int(setup.group(1)) != 0 or int(hold.group(1)) != 0:
        return Check("timing", FAIL, detail + "; reported violations nonzero",
                     [str(report[0])])
    if float(worst.group(1)) < 0:
        return Check("timing", FAIL, detail + "; negative worst slack",
                     [str(report[0])])
    return Check("timing", PASS, detail + "; declared checks met at the executed target",
                 [str(report[0])])


def check_timing_coverage(audit: dict[str, Any] | None) -> Check:
    if audit is None:
        return Check("timing_coverage", UNKNOWN,
                     "no timing-unit audit; coverage and unconstrained endpoints unknown")
    cov = audit.get("coverage") or {}
    unconstrained = cov.get("unconstrained_endpoints")
    if unconstrained is None:
        return Check("timing_coverage", UNKNOWN,
                     "audit does not record unconstrained endpoints")
    detail = (f"inputs={cov.get('input_ports')} outputs={cov.get('output_ports')} "
              f"registers={cov.get('registers')} clocks={cov.get('clocks')} "
              f"unconstrained={unconstrained}")
    if int(unconstrained) != 0:
        return Check("timing_coverage", FAIL, detail + "; unconstrained endpoints present")
    if not cov.get("registers"):
        return Check("timing_coverage", FAIL,
                     detail + "; no sequential endpoints, so timing closure is not "
                     "demonstrated by this design")
    return Check("timing_coverage", PASS, detail)


def check_parasitics(view: RunView, audit: dict[str, Any] | None) -> Check:
    spef = view.find(view.results, "6_final.spef")
    log = view.evidence / "stage_finish.log"
    if not spef:
        return Check("extraction", FAIL, "6_final.spef missing")
    if spef[0].stat().st_size == 0:
        return Check("extraction", FAIL, "6_final.spef is empty", [str(spef[0])])
    text = read_text(log)
    rcx = RCX_RE.search(text)
    if not rcx or int(rcx.group(1)) == 0:
        return Check("extraction", FAIL,
                     "finish log has no positive RCX extraction record; "
                     "SPEF presence alone does not prove extraction ran",
                     [str(log)])
    if audit is None:
        return Check("extraction", UNKNOWN,
                     f"SPEF present ({spef[0].stat().st_size} bytes), RCX extracted "
                     f"{rcx.group(1)} nets, but annotation coverage was not audited",
                     [str(spef[0])])
    par = audit.get("parasitics") or {}
    unannotated = par.get("unannotated_drivers")
    if unannotated is None:
        return Check("extraction", UNKNOWN,
                     "audit does not record parasitic annotation coverage")
    if int(unannotated) != 0:
        return Check("extraction", FAIL,
                     f"{unannotated} unannotated drivers after reading SPEF",
                     [str(spef[0])])
    return Check("extraction", PASS,
                 f"SPEF {spef[0].stat().st_size} bytes; RCX {rcx.group(1)} nets; "
                 f"0 unannotated drivers", [str(spef[0])])


# --------------------------------------------------------------------------
# aggregate
# --------------------------------------------------------------------------
def verify_run(run_dir: str | Path, audit: dict[str, Any] | None = None,
               require_endpoint: bool = True) -> dict[str, Any]:
    view = load_run(run_dir)
    checks = [
        check_execution(view),
        check_artifacts(view) if require_endpoint else
        Check("artifacts", NOT_EVALUATED, "endpoint artifacts not required"),
        check_stale_reports(view),
        check_routing(view),
        check_timing(view, audit),
        check_timing_coverage(audit),
        check_parasitics(view, audit),
    ]
    statuses = [c.status for c in checks]
    if FAIL in statuses:
        overall = FAIL
    elif UNKNOWN in statuses:
        overall = UNKNOWN
    elif all(s == PASS for s in statuses):
        overall = PASS
    else:
        overall = NOT_EVALUATED
    return {"run_id": view.run.get("run_id") or view.run_dir.name,
            "run_dir": str(view.run_dir), "overall": overall,
            "checks": [c.as_dict() for c in checks],
            "audit_supplied": audit is not None}


# --------------------------------------------------------------------------
# recovery
# --------------------------------------------------------------------------
def verify_recovery(baseline: dict[str, Any], failure: dict[str, Any],
                    recovery: dict[str, Any], *,
                    approval_apply: dict[str, Any] | None = None,
                    targeted_marker: str | None = None) -> dict[str, Any]:
    checks: list[Check] = []

    # 1. The approved operation reached the executed configuration.
    if approval_apply is None:
        checks.append(Check("approved_change_reached", UNKNOWN,
                            "no approval_apply.json supplied"))
    else:
        phase = approval_apply.get("phase")
        after = approval_apply.get("after_sha256")
        if phase not in ("applied", "verified") or not after:
            checks.append(Check("approved_change_reached", FAIL,
                                f"apply phase={phase!r}; after_sha256={after!r}"))
        else:
            checks.append(Check("approved_change_reached", PASS,
                                f"phase={phase}; after_sha256={after[:16]}",
                                [str(approval_apply.get("target"))]))

    # 2. The targeted failure disappeared from the recovery evidence.
    failure_view = load_run(failure.get("run_dir", ""))
    recovery_view = load_run(recovery.get("run_dir", ""))
    if targeted_marker:
        marker = targeted_marker.lower()
        still = []
        for log in sorted(recovery_view.evidence.glob("stage_*.log")):
            if marker in read_text(log).lower():
                still.append(log.name)
        if still:
            checks.append(Check("target_failure_cleared", FAIL,
                                f"marker {targeted_marker!r} still present in {still}"))
        else:
            checks.append(Check("target_failure_cleared", PASS,
                                f"marker {targeted_marker!r} absent from recovery logs"))
    else:
        fail_stage = failure.get("first_failed_stage")
        rec_stages = {s["stage"]: int(s["rc"]) for s in
                      (recovery_view.run.get("stages") or [])}
        if not fail_stage:
            checks.append(Check("target_failure_cleared", UNKNOWN,
                                "failure run has no recorded failed stage"))
        elif rec_stages.get(fail_stage) == 0:
            checks.append(Check("target_failure_cleared", PASS,
                                f"stage {fail_stage} rc=0 in recovery"))
        else:
            checks.append(Check("target_failure_cleared", FAIL,
                                f"stage {fail_stage} rc={rec_stages.get(fail_stage)} "
                                f"in recovery"))

    # 3. Every affected downstream stage ran or was validly reused.
    scope = approval_apply.get("rerun_scope") if approval_apply else None
    rec_stages = {s["stage"]: int(s["rc"]) for s in
                  (recovery_view.run.get("stages") or [])}
    if not scope:
        checks.append(Check("downstream_scope", UNKNOWN,
                            "no approved rerun scope recorded"))
    else:
        missing = [s for s in scope if s not in rec_stages]
        failed = [s for s in scope if rec_stages.get(s, 0) != 0]
        if missing or failed:
            checks.append(Check("downstream_scope", FAIL,
                                f"scope={scope}; missing={missing}; failed={failed}"))
        else:
            checks.append(Check("downstream_scope", PASS,
                                f"all {len(scope)} affected stages rc=0: {scope}"))

    # 4. No collateral regression against the baseline.
    b = {c["name"]: c["status"] for c in baseline.get("checks", [])}
    r = {c["name"]: c["status"] for c in recovery.get("checks", [])}
    regressed = [name for name, status in r.items()
                 if status == FAIL and b.get(name) == PASS]
    if baseline.get("overall") != PASS:
        checks.append(Check("collateral_regression", FAIL,
                            f"baseline itself is {baseline.get('overall')}; "
                            "a recovery cannot be accepted against a reference "
                            "that does not pass"))
    elif regressed:
        checks.append(Check("collateral_regression", FAIL,
                            f"recovery regressed checks that passed in baseline: {regressed}"))
    elif recovery.get("overall") != PASS:
        checks.append(Check("collateral_regression", FAIL,
                            f"recovery overall={recovery.get('overall')}; "
                            "cannot claim a clean recovery"))
    else:
        checks.append(Check("collateral_regression", PASS,
                            "recovery passes every check the baseline passes"))

    # 5. A recovery is only meaningful if it actually executed.
    if recovery.get("overall") == PASS and failure.get("overall") == PASS:
        checks.append(Check("failure_is_real", FAIL,
                            "failure run passed verification; nothing was recovered"))
    else:
        checks.append(Check("failure_is_real", PASS,
                            f"failure overall={failure.get('overall')}"))

    statuses = [c.status for c in checks]
    if FAIL in statuses:
        overall = FAIL
    elif UNKNOWN in statuses:
        overall = UNKNOWN
    else:
        overall = PASS
    return {"overall": overall, "checks": [c.as_dict() for c in checks],
            "baseline": baseline.get("run_id"),
            "failure": failure.get("run_id"),
            "recovery": recovery.get("run_id")}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def _load_audit(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run")
    p.add_argument("--audit")
    p.add_argument("--baseline")
    p.add_argument("--failure")
    p.add_argument("--recovery")
    p.add_argument("--audit-map",
                   help="JSON {run_id_or_path: audit_path} for the recovery mode")
    p.add_argument("--approval-apply")
    p.add_argument("--targeted-marker")
    p.add_argument("--out")
    args = p.parse_args()

    if args.run:
        out: dict[str, Any] = verify_run(args.run, _load_audit(args.audit))
    else:
        if not (args.baseline and args.failure and args.recovery):
            p.error("--run, or all of --baseline/--failure/--recovery, is required")
        amap = json.loads(Path(args.audit_map).read_text(encoding="utf-8")) \
            if args.audit_map else {}

        def audit_for(path: str) -> dict[str, Any] | None:
            entry = amap.get(path) or amap.get(Path(path).name)
            return _load_audit(entry) if entry else None

        b = verify_run(args.baseline, audit_for(args.baseline))
        f = verify_run(args.failure, audit_for(args.failure))
        r = verify_run(args.recovery, audit_for(args.recovery))
        ap = json.loads(Path(args.approval_apply).read_text(encoding="utf-8")) \
            if args.approval_apply else None
        out = {"baseline": b, "failure": f, "recovery": r,
               "recovery_verdict": verify_recovery(
                   b, f, r, approval_apply=ap,
                   targeted_marker=args.targeted_marker)}

    text = json.dumps(out, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if (out.get("overall") or out["recovery_verdict"]["overall"]) == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
