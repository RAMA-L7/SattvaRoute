#!/usr/bin/env python3
"""Fixtures for the strict run verifier (offline, no EDA).

Each test builds a synthetic run tree that reproduces one failure mode the
verifier must not wave through, plus one clean run that must pass. The point of
the suite is the *negative* cases: an empty report, an early zero count, stale
reports, absent units and identical incomplete runs.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from verify_run import FAIL, PASS, UNKNOWN, verify_recovery, verify_run  # noqa: E402

FINISH_TEMPLATE = """finish report_tns
tns max 0.00
finish report_wns
wns max 0.00
finish report_worst_slack
worst slack max {slack}
finish report_clock_min_period
clk period_min = {period_min} fmax = {fmax}
finish setup_violation_count
setup violation count {setup}
finish hold_violation_count
hold violation count {hold}
"""

AUDIT = {
    "units": {"time": "1ns", "capacitance": "1fF", "resistance": "1kohm"},
    "clock": {"name": "clk", "period": 1000.0, "waveform": [0.0, 500.0]},
    "slack": {"max": 899.75, "min": 99.98},
    "period_min": {"reg_to_reg": {"period_min": 0.0, "fmax": None},
                   "including_ports": {"period_min": 100.25, "fmax": "9.97"}},
    "coverage": {"input_ports": 73, "output_ports": 32, "registers": 1,
                 "clocks": 1, "unconstrained_endpoints": 0},
    "parasitics": {"unannotated_drivers": 0, "partially_unannotated_drivers": 0},
}


def make_run(root: Path, *, name="run", stages_rc=0, artifacts=True,
             drt_counts=(0,), drc_bytes=0, slack=899.75, setup=0, hold=0,
             finish=True, period_min=100.25, spef=True, rcx_nets=209,
             report_age_s=60) -> Path:
    run = root / name
    ev = run / "evidence"
    res = run / "work" / "results" / "nangate45" / "design" / "base"
    rep = run / "work" / "reports" / "nangate45" / "design" / "base"
    for d in (ev, res, rep):
        d.mkdir(parents=True, exist_ok=True)

    start = datetime.now(timezone.utc) - timedelta(seconds=600)
    end = start + timedelta(seconds=300)
    stages = [{"stage": "synth", "rc": stages_rc, "start": start.isoformat(),
               "end": end.isoformat()}]
    if stages_rc == 0:
        stages.append({"stage": "route", "rc": 0,
                       "start": end.isoformat(), "end": end.isoformat()})
    (ev / "run.json").write_text(json.dumps({
        "run_id": name, "run_dir": str(run), "overall_rc": stages_rc,
        "first_failed_stage": None if stages_rc == 0 else "synth",
        "stages": stages}), encoding="utf-8")
    for s in stages:
        (ev / f"stage_{s['stage']}.log").write_text("log\n", encoding="utf-8")

    route = ev / "stage_route.log"
    route.write_text("".join(
        f"[INFO DRT-0199]   Number of violations = {n}.\n" for n in drt_counts)
        + ("write_db 5_2_route.odb\nfillcell.tcl\n" if drt_counts else ""),
        encoding="utf-8")
    (ev / "stage_finish.log").write_text(
        f"[INFO RCX-0045] Extract {rcx_nets} nets, 677 rsegs, 677 caps, 1998 ccs\n",
        encoding="utf-8")

    if artifacts:
        for n in ("5_route.odb", "route.guide", "6_final.odb", "6_final.def",
                  "6_final.gds", "6_final.v", "6_final.sdc"):
            (res / n).write_bytes(b"x" * 16)
        if spef:
            (res / "6_final.spef").write_bytes(b"x" * 16)
        (res / "clock_period.txt").write_text("1000\n", encoding="utf-8")
        (rep / "5_route_drc.rpt").write_bytes(b"x" * drc_bytes)
        if finish:
            (rep / "6_finish.rpt").write_text(FINISH_TEMPLATE.format(
                slack=slack, period_min=period_min,
                fmax="9.97" if period_min else "inf",
                setup=setup, hold=hold), encoding="utf-8")
        stamp = (datetime.now(timezone.utc) - timedelta(seconds=report_age_s)).timestamp()
        for p in (rep / "5_route_drc.rpt", rep / "6_finish.rpt"):
            if p.exists():
                os.utime(p, (stamp, stamp))
    return run


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def status(self, run, audit=AUDIT):
        return verify_run(run, audit)

    def check(self, out, name):
        return next(c for c in out["checks"] if c["name"] == name)["status"]

    # ---- positive control -------------------------------------------------
    def test_clean_run_passes(self):
        out = self.status(make_run(self.root))
        self.assertEqual(out["overall"], PASS, out)

    # ---- missing endpoint artifacts --------------------------------------
    def test_both_runs_missing_endpoint_artifacts_fail(self):
        a = self.status(make_run(self.root, name="a", artifacts=False))
        b = self.status(make_run(self.root, name="b", artifacts=False))
        self.assertEqual(a["overall"], FAIL)
        self.assertEqual(b["overall"], FAIL)
        self.assertEqual(self.check(a, "artifacts"), FAIL)

    # ---- early zero then final nonzero ------------------------------------
    def test_early_zero_then_final_nonzero_fails(self):
        run = make_run(self.root, drt_counts=(0, 0, 3))
        out = self.status(run)
        self.assertEqual(self.check(out, "routing"), FAIL)
        self.assertEqual(out["overall"], FAIL)

    def test_last_zero_after_early_nonzero_passes(self):
        run = make_run(self.root, drt_counts=(164, 40, 25, 2, 0))
        self.assertEqual(self.check(self.status(run), "routing"), PASS)

    # ---- stale reports ----------------------------------------------------
    def test_stale_report_fails(self):
        run = make_run(self.root, report_age_s=3600)
        out = self.status(run)
        self.assertEqual(self.check(out, "report_freshness"), FAIL)
        self.assertEqual(out["overall"], FAIL)

    # ---- units ------------------------------------------------------------
    def test_missing_units_is_unknown_not_pass(self):
        run = make_run(self.root)
        out = verify_run(run, audit=None)
        self.assertEqual(self.check(out, "timing"), UNKNOWN)
        self.assertEqual(out["overall"], UNKNOWN)

    def test_audit_without_time_unit_is_unknown(self):
        run = make_run(self.root)
        audit = json.loads(json.dumps(AUDIT))
        audit["units"] = {}
        out = verify_run(run, audit)
        self.assertEqual(self.check(out, "timing"), UNKNOWN)

    # ---- unconstrained ----------------------------------------------------
    def test_unconstrained_endpoints_fail_coverage(self):
        run = make_run(self.root)
        audit = json.loads(json.dumps(AUDIT))
        audit["coverage"]["unconstrained_endpoints"] = 4
        out = verify_run(run, audit)
        self.assertEqual(self.check(out, "timing_coverage"), FAIL)
        self.assertEqual(out["overall"], FAIL)

    # ---- nonzero violations with rc 0 ------------------------------------
    def test_nonzero_violations_with_rc_zero_fails(self):
        run = make_run(self.root, drt_counts=(0,), drc_bytes=120)
        out = self.status(run)
        self.assertEqual(self.check(out, "routing"), FAIL)
        self.assertEqual(out["overall"], FAIL)

    def test_timing_violation_with_rc_zero_fails(self):
        run = make_run(self.root, setup=2)
        out = self.status(run)
        self.assertEqual(self.check(out, "timing"), FAIL)
        self.assertEqual(out["overall"], FAIL)

    # ---- incomplete extraction -------------------------------------------
    def test_incomplete_extraction_fails(self):
        run = make_run(self.root, spef=False)
        out = self.status(run)
        self.assertEqual(self.check(out, "extraction"), FAIL)
        self.assertEqual(out["overall"], FAIL)

    def test_unannotated_parasitics_fail(self):
        run = make_run(self.root)
        audit = json.loads(json.dumps(AUDIT))
        audit["parasitics"]["unannotated_drivers"] = 12
        out = verify_run(run, audit)
        self.assertEqual(self.check(out, "extraction"), FAIL)

    def test_zero_net_extraction_fails(self):
        run = make_run(self.root, rcx_nets=0)
        self.assertEqual(self.check(self.status(run), "extraction"), FAIL)

    # ---- missing timing report -------------------------------------------
    def test_missing_finish_report_is_unknown(self):
        run = make_run(self.root, finish=False)
        out = self.status(run)
        self.assertEqual(self.check(out, "timing"), UNKNOWN)

    # ---- recovery ---------------------------------------------------------
    def _recovery_inputs(self):
        base = self.status(make_run(self.root, name="base"))
        fail = verify_run(make_run(self.root, name="fail", stages_rc=2,
                                   artifacts=False, drt_counts=()), None)
        rec = self.status(make_run(self.root, name="rec"))
        return base, fail, rec

    def test_recovery_passes_when_scope_ran_and_marker_gone(self):
        base, fail, rec = self._recovery_inputs()
        apply = {"phase": "verified", "after_sha256": "a" * 64,
                 "rerun_scope": ["synth", "route"], "target": "config.mk"}
        out = verify_recovery(base, fail, rec, approval_apply=apply,
                              targeted_marker="missing_fakeram")
        self.assertEqual(out["overall"], PASS, out)

    def test_recovery_fails_when_marker_still_present(self):
        base, fail, rec = self._recovery_inputs()
        (Path(rec["run_dir"]) / "evidence" / "stage_synth.log").write_text(
            "No such file: missing_fakeram45_64x32.lib\n", encoding="utf-8")
        apply = {"phase": "verified", "after_sha256": "a" * 64,
                 "rerun_scope": ["synth", "route"], "target": "config.mk"}
        out = verify_recovery(base, fail, rec, approval_apply=apply,
                              targeted_marker="missing_fakeram")
        self.assertEqual(out["overall"], FAIL)

    def test_recovery_fails_when_scope_stage_missing(self):
        base, fail, rec = self._recovery_inputs()
        apply = {"phase": "verified", "after_sha256": "a" * 64,
                 "rerun_scope": ["synth", "floorplan", "route"],
                 "target": "config.mk"}
        out = verify_recovery(base, fail, rec, approval_apply=apply,
                              targeted_marker="missing_fakeram")
        self.assertEqual(out["overall"], FAIL)

    def test_recovery_fails_without_approval_record(self):
        base, fail, rec = self._recovery_inputs()
        out = verify_recovery(base, fail, rec, approval_apply=None,
                              targeted_marker="missing_fakeram")
        self.assertEqual(out["overall"], UNKNOWN)

    def test_recovery_fails_when_baseline_is_broken(self):
        base = self.status(make_run(self.root, name="base", setup=5))
        fail = verify_run(make_run(self.root, name="fail", stages_rc=2,
                                   artifacts=False, drt_counts=()), None)
        rec = self.status(make_run(self.root, name="rec"))
        apply = {"phase": "verified", "after_sha256": "a" * 64,
                 "rerun_scope": ["synth", "route"], "target": "config.mk"}
        out = verify_recovery(base, fail, rec, approval_apply=apply,
                              targeted_marker="missing_fakeram")
        self.assertEqual(out["overall"], FAIL)

    def test_failure_run_that_passes_is_not_a_recovery(self):
        base = self.status(make_run(self.root, name="base"))
        fail = self.status(make_run(self.root, name="fail"))
        rec = self.status(make_run(self.root, name="rec"))
        apply = {"phase": "verified", "after_sha256": "a" * 64,
                 "rerun_scope": ["synth", "route"], "target": "config.mk"}
        out = verify_recovery(base, fail, rec, approval_apply=apply,
                              targeted_marker="missing_fakeram")
        self.assertEqual(out["overall"], FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
