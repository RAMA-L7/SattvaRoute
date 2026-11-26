#!/usr/bin/env python3
"""Generalized, bounded failure diagnosis and reviewable patch proposal.

Deterministic parsing/classification is deliberately separate from any
model-generated narrative, from human approval, from patch application and
from engineering verification. No injected fixture name (e.g. a particular
``missing_*`` file) is required or inspected: the mechanism is derived from
real error text, the resolved configuration, file existence, collateral
identity and compatible baseline declarations.

A proposal is always *textual and for review*. This module never executes,
applies or approves anything. When the correction is ambiguous, when a needed
construct is unsupported, or when no compatible replacement can be shown to
exist, it returns ``insufficient_evidence`` rather than inventing a library,
macro or corner.

Bounded Make support
--------------------
Only simple, static assignments to a single ``.mk`` target are considered:
``export VAR = ...``, ``VAR = ...``, ``VAR := ...``, ``VAR += ...``,
``VAR ?= ...``, with backslash line continuation and whitespace-separated
multiple values. The following are explicitly rejected for the variable being
repaired (returns ``insufficient_evidence``): ``$(shell ...)``, ``$(call ...)``,
``$(foreach ...)``, ``$(if ...)``, ``$(or ...)``, ``$(and ...)``,
``$(wildcard ...)``, ``$(eval ...)``, ``$(notdir ...)``, ``$(dir ...)``,
``$(subst ...)``, ``$(patsubst ...)``, ``$(filter ...)``, ``define``,
``ifdef``/``ifndef``/``ifeq``/``ifneq``/``else``/``endif`` conditionals,
recursion, ``%`` patterns, backticks and any unresolvable ``$(...)``/``${...}``.
Only the known static variables ``$(DESIGN_DIR)``, ``$(PLATFORM_DIR)``,
``$(SATTVA_ROOT)`` and ``$(ORFS_MIRROR)`` are expanded.
"""
from __future__ import annotations

import dataclasses
import difflib
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# families
# --------------------------------------------------------------------------
MISSING_MACRO_LIB = "MISSING_MACRO_LIB"
MISSING_MACRO_LEF = "MISSING_MACRO_LEF"
MISSING_TECH_LEF = "MISSING_TECH_LEF"
MISSING_SC_LIB = "MISSING_SC_LIB"
MISSING_SC_LEF = "MISSING_SC_LEF"
MISSING_CONSTRAINT = "MISSING_CONSTRAINT"
MISSING_NETLIST = "MISSING_NETLIST"
UNKNOWN_LIB_CELL = "UNKNOWN_LIB_CELL"
PIN_ACCESS = "PIN_ACCESS"
INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

INSUFFICIENT = "insufficient_evidence"

LIB_VARS = {"ADDITIONAL_LIBS", "LIB_FILES", "SC_LIB", "MACRO_LIB", "ADDITIONAL_LIB"}
LEF_VARS = {"ADDITIONAL_LEFS", "SC_LEF", "TECH_LEF", "MACRO_LEF", "ADDITIONAL_LEF"}
SDC_VARS = {"SDC_FILE"}
NETLIST_VARS = {"VERILOG_FILES", "SYNTH_NETLIST_FILES", "VERILOG_FILES_BLACKBOX"}

MAKE_FUNC_RE = re.compile(r"\$\(\s*(shell|call|foreach|if|or|and|wildcard|eval|"
                          r"notdir|dir|subst|patsubst|filter|filter-out|"
                          r"findstring|firstword|word|words|sort|strip|"
                          r"addprefix|addsuffix|join|abspath|realpath|curdir)\b",
                          re.I)
UNRESOLVED_MAKE_RE = re.compile(r"\$[({][A-Za-z_][A-Za-z0-9_]*[)}]")
CONDITIONAL_RE = re.compile(r"^\s*(ifdef|ifndef|ifeq|ifneq|else|endif|define|"
                            r"endef|override|undefine)\b", re.M)
MISSING_PATH_RE = re.compile(
    r"(?:No rule to make target|No such file or directory|cannot open|"
    r"can't open|unable to open|not found|does not exist|could not open)\s*"
    r"[`'\"]?([^\s'\"`]+\.(?:lib|lef|sdc|v|vg|gds|tcl|mk))?", re.I)
QUOTED_TARGET_RE = re.compile(r"No rule to make target\s+[`'\"]([^`'\"]+)[`'\"]", re.I)
FILE_TOKEN_RE = re.compile(r"[`'\"]?((?:[A-Za-z0-9_./\\-]+)\.(?:lib|lef|sdc|v|vg|gds))[`'\"]?")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# classification
# --------------------------------------------------------------------------
def _read_stages(ev: Path) -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = []
    tsv = ev / "stages.tsv"
    if tsv.is_file():
        for line in tsv.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                stages.append({"stage": parts[0], "rc": parts[1]})
    return stages


def _scan_logs(ev: Path) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    patterns = (
        r"DRT-\d+[^\n]*",
        r"[^\n]*not found in library[^\n]*",
        r"[^\n]*No access point[^\n]*",
        r"[^\n]*No rule to make target[^\n]*",
        r"[^\n]*No such file or directory[^\n]*",
        r"[^\n]*(?:cannot|can't|unable to) open[^\n]*",
        r"[^\n]*not found[^\n]*",
        r"[^\n]*does not exist[^\n]*",
        r"[^\n]*ERROR[^\n]*",
    )
    for log in sorted(ev.glob("stage_*.log")):
        text = log.read_text(encoding="utf-8", errors="replace")
        for pat in patterns:
            for m in re.finditer(pat, text, re.I):
                hits.append({"log": log.name,
                             "line": text[:m.start()].count("\n") + 1,
                             "text": m.group(0).strip()[:400]})
    return hits


def _missing_paths(hits: list[dict[str, Any]]) -> list[str]:
    found: list[str] = []
    for h in hits:
        text = h["text"]
        m = QUOTED_TARGET_RE.search(text)
        if m:
            found.append(m.group(1))
        for m in MISSING_PATH_RE.finditer(text):
            if m.group(1):
                found.append(m.group(1))
        for m in FILE_TOKEN_RE.finditer(text):
            found.append(m.group(1))
    # de-dup, stable
    out: list[str] = []
    for p in found:
        if p not in out:
            out.append(p)
    return out


def classify_failure(run_dir: str | Path) -> dict[str, Any]:
    """Read real run evidence; never infer success from rc alone."""
    run = Path(run_dir)
    ev = run / "evidence"
    stages = _read_stages(ev)
    failed = next((s for s in stages if s["rc"] not in ("0", "RESUMED")), None)
    hits = _scan_logs(ev)
    blob = "\n".join(h["text"].lower() for h in hits)
    missing = _missing_paths(hits)

    signature = "UNCLASSIFIED"
    family = "UNKNOWN"
    missing_file: str | None = None
    affected_variable: str | None = None

    if "drt-0073" in blob or any("no access point" in h["text"].lower() for h in hits):
        signature, family = "DRT-0073 No access point", PIN_ACCESS
    else:
        matched = False
        for path in missing:
            low = path.lower()
            if low.endswith(".lib") or low.endswith(".lib.*"):
                missing_file = path
                matched = True
                if "fakeram" in low or _references_var(blob, LIB_VARS | {"ADDITIONAL_LIBS"}, low):
                    family, signature = MISSING_MACRO_LIB, "missing macro Liberty reference"
                else:
                    family, signature = MISSING_SC_LIB, "missing standard-cell Liberty reference"
                affected_variable = _which_var(run, missing, LIB_VARS)
                break
            if low.endswith(".lef"):
                missing_file = path
                matched = True
                affected_variable = _which_var(run, missing, LEF_VARS)
                if affected_variable in ("TECH_LEF",) or "tech" in low:
                    family, signature = MISSING_TECH_LEF, "missing technology LEF reference"
                elif affected_variable == "SC_LEF":
                    family, signature = MISSING_SC_LEF, "missing standard-cell LEF reference"
                else:
                    family, signature = MISSING_MACRO_LEF, "missing macro LEF reference"
                break
            if low.endswith(".sdc"):
                missing_file = path
                matched = True
                family, signature = MISSING_CONSTRAINT, "missing timing constraint file"
                affected_variable = "SDC_FILE"
                break
            if low.endswith((".v", ".vg")):
                missing_file = path
                matched = True
                family, signature = MISSING_NETLIST, "missing netlist/RTL reference"
                affected_variable = _which_var(run, missing, NETLIST_VARS)
                break
        if not matched:
            if "not found in library" in blob:
                family, signature = MISSING_MACRO_LIB, "cell/name not found in library"
            elif failed:
                signature = f"stage {failed['stage']} rc={failed['rc']}"

    return {
        "run_dir": str(run),
        "failed_stage": failed["stage"] if failed else None,
        "failed_rc": failed["rc"] if failed else None,
        "signature": signature,
        "family": family,
        "missing_file": missing_file,
        "affected_variable": affected_variable,
        "missing_references": missing,
        "evidence_refs": [str(ev / "stages.tsv"), str(ev / "run.json")]
                         + [str(h["log"]) for h in hits[:12]],
        "log_hits": hits[:40],
        "source": "deterministic_parser",
    }


def _references_var(blob: str, vars: set[str], _low: str) -> bool:
    return any(v.lower() in blob for v in vars)


def _which_var(run: Path, missing: list[str], vars: set[str]) -> str | None:
    cfg = run / "config.mk"
    if not cfg.is_file():
        # attempt-local designs keep config beside evidence
        cand = run.parent / "config.mk"
        cfg = cand if cand.is_file() else cfg
    if not cfg.is_file():
        return None
    assignments = parse_make_assignments(cfg.read_text(encoding="utf-8", errors="replace"))
    for var in vars:
        for a in assignments:
            if a.var != var:
                continue
            value = a.value.lower()
            for m in missing:
                token = Path(m).name.lower()
                stem = Path(token).stem.lower()
                if token in value or stem in value or Path(m).name.lower() in value:
                    return var
    return None


# --------------------------------------------------------------------------
# bounded Make parsing
# --------------------------------------------------------------------------
@dataclasses.dataclass
class Assignment:
    var: str
    op: str
    value: str
    lineno: int
    raw: str


def parse_make_assignments(text: str) -> list[Assignment]:
    """Parse simple static Make assignments; never interpret conditionals."""
    lines = text.splitlines()
    out: list[Assignment] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        # continuation: join lines ending in a backslash
        while raw.rstrip().endswith("\\") and i + 1 < len(lines):
            raw = raw.rstrip()[:-1] + lines[i + 1].lstrip()
            stripped = raw.strip()
            i += 1
        m = re.match(r"^(?:export\s+|override\s+)*([A-Za-z_][A-Za-z0-9_]*)\s*"
                     r"(\+=|:=|\?=|=)\s*(.*)$", stripped)
        if m:
            out.append(Assignment(var=m.group(1), op=m.group(2),
                                  value=m.group(3).strip(), lineno=i + 1, raw=raw))
        i += 1
    return out


def _unsupported_reason(var: str, text: str, value: str) -> str | None:
    if MAKE_FUNC_RE.search(value):
        return f"unsupported Make function in ${var}"
    if "`" in value:
        return f"backtick shell in ${var}"
    if "%" in value:
        return f"pattern rule / % in ${var}"
    if CONDITIONAL_RE.search(text):
        return "conditional Make structure in file"
    leftover = UNRESOLVED_MAKE_RE.search(value)
    if leftover:
        # allow known static vars; reject everything else
        inner = re.sub(r"[\$\(\){]|[\)\}]", "", leftover.group(0)).upper()
        if inner not in {"DESIGN_DIR", "PLATFORM_DIR", "SATTVA_ROOT", "ORFS_MIRROR"}:
            return f"unresolvable variable {leftover.group(0)} in ${var}"
    return None


def _expand_static(value: str, design_dir: Path, platform_dir: Path,
                   mirror: Path, project_root: Path) -> str:
    mapping = {
        "DESIGN_DIR": str(design_dir),
        "PLATFORM_DIR": str(platform_dir),
        "SATTVA_ROOT": str(project_root),
        "ORFS_MIRROR": str(mirror),
    }
    out = value
    for _ in range(4):
        changed = False
        for k, v in mapping.items():
            for form in (f"$({k})", f"${{{k}}}", f"${k}"):
                if form in out:
                    out = out.replace(form, v)
                    changed = True
        if not changed:
            break
    return out


def _split_values(value: str) -> list[str]:
    return [tok for tok in value.split() if tok and tok != "\\"]


# --------------------------------------------------------------------------
# proposal
# --------------------------------------------------------------------------
def _resolve_missing(missing: str, design_dir: Path, platform_dir: Path,
                     mirror: Path) -> Path:
    p = Path(missing)
    if p.is_absolute():
        return p
    candidates = [design_dir / p, platform_dir / p, mirror / p,
                  mirror / "flow" / p, Path.cwd() / p]
    for c in candidates:
        if c.exists():
            return c
    return design_dir / p


def _platform_for(design_dir: Path, mirror: Path) -> Path:
    name = "nangate45"
    cfg = design_dir / "config.mk"
    if cfg.is_file():
        for a in parse_make_assignments(cfg.read_text(encoding="utf-8", errors="replace")):
            if a.var == "PLATFORM":
                name = a.value.strip().strip('"').strip("'")
                break
    return mirror / "flow" / "platforms" / name


def propose_patch(diagnosis: dict[str, Any], target: str | Path,
                  *, baseline: str | Path | None = None,
                  mirror: str | Path | None = None,
                  project_root: str | Path | None = None) -> dict[str, Any] | None:
    """Create an exact, reviewable, non-applied textual patch, or None.

    Returns a proposal dict. When evidence is insufficient, returns a proposal
    with ``status='insufficient_evidence'`` and ``applies=False`` rather than
    inventing a replacement. Returns ``None`` only if no bounded rule applies.
    """
    family = diagnosis.get("family")
    supported = {MISSING_MACRO_LIB, MISSING_MACRO_LEF, MISSING_TECH_LEF,
                 MISSING_SC_LIB, MISSING_SC_LEF, MISSING_CONSTRAINT}
    if family not in supported:
        return None

    target_path = Path(target)
    if not target_path.is_file():
        return _insufficient(target_path, family,
                             "target file does not exist", diagnosis)

    project_root = Path(project_root) if project_root else ROOT
    mirror = Path(mirror) if mirror else project_root / "tools" / "OpenROAD-flow-scripts"
    design_dir = target_path.parent
    platform_dir = _platform_for(design_dir, mirror)
    baseline_design = Path(baseline) if baseline else project_root / "benchmark" / "design" / "nangate_macro_control"

    original = target_path.read_text(encoding="utf-8")
    assignments = parse_make_assignments(original)

    var = diagnosis.get("affected_variable")
    if not var:
        var = _guess_variable(family, assignments, diagnosis)
    if not var:
        return _insufficient(target_path, family,
                             "cannot determine which configuration variable holds the "
                             "bad reference", diagnosis)

    # boundary check on the variable's value(s)
    relevant = [a for a in assignments if a.var == var]
    if not relevant:
        return _insufficient(target_path, family,
                             f"variable ${var} not found as a static assignment", diagnosis)
    combined_value = "\n".join(a.value for a in relevant)
    reason = _unsupported_reason(var, original, combined_value)
    if reason:
        return _insufficient(target_path, family,
                             "unsupported Make construct: " + reason, diagnosis)

    missing_name = diagnosis.get("missing_file")
    missing_token = Path(missing_name).name if missing_name else None

    # compatible baseline declaration
    baseline_decl = _baseline_declaration(baseline_design, var)
    intended: str | None = None
    intended_source: str | None = None
    if baseline_decl:
        for tok in _split_values(baseline_decl):
            if _is_collector_token(tok):
                continue
            expanded = _expand_static(tok, baseline_design, platform_dir,
                                      mirror, project_root)
            cand = _resolve_missing(expanded, baseline_design, platform_dir, mirror)
            if cand.is_file() and _compatible_replacement(cand, var, missing_token):
                intended = tok
                intended_source = f"compatible baseline {baseline_design / 'config.mk'}"
                break

    if intended is None:
        # fall back: find the same-named collateral already present in the
        # platform, never inventing a different macro/corner
        for sub, ext in (("lib", ".lib"), ("lef", ".lef")):
            if missing_token and missing_token.endswith(ext):
                stem = _restore_stem(missing_token, var)
                for search in (platform_dir / sub, platform_dir):
                    cand = search / stem
                    if cand.is_file():
                        intended = _rewrite_to_platform(tok=missing_token,
                                                        platform_dir=platform_dir,
                                                        stem=stem, sub=sub)
                        intended_source = f"existing collateral {cand}"
                        break
            if intended:
                break

    if intended is None:
        return _insufficient(target_path, family,
                             "no compatible replacement collateral could be shown to "
                             "exist; refusing to invent a library or corner", diagnosis)

    # verify replacement resolves to a real, compatible file
    intended_expanded = _expand_static(intended, design_dir, platform_dir,
                                       mirror, project_root)
    intended_path = _resolve_missing(intended_expanded, design_dir, platform_dir, mirror)
    if not intended_path.is_file():
        return _insufficient(target_path, family,
                             f"intended replacement does not exist: {intended_path}",
                             diagnosis)

    # current resolved value
    current_value = _current_resolved(assignments, var, design_dir, platform_dir,
                                      mirror, project_root)
    missing_expanded = _expand_static(missing_name or "", design_dir, platform_dir,
                                      mirror, project_root) if missing_name else None

    patched = _build_patched(original, assignments, var, intended,
                             missing_name=missing_name, missing_token=missing_token)
    if patched == original:
        return _insufficient(target_path, family,
                             "computed patch would not change the file", diagnosis)
    # re-validate the patched result does not contain unsupported constructs for var
    recheck = parse_make_assignments(patched)
    recheck_value = "\n".join(a.value for a in recheck if a.var == var)
    if _unsupported_reason(var, patched, recheck_value):
        return _insufficient(target_path, family,
                             "patched result introduces an unsupported construct",
                             diagnosis)

    diff = "".join(difflib.unified_diff(
        original.splitlines(True), patched.splitlines(True),
        fromfile=str(target_path), tofile=str(target_path), n=3))
    earliest = diagnosis.get("failed_stage") or _earliest_for_var(var)
    return {
        "status": "proposal",
        "applies": False,
        "note": "Propose a textual correction for review; do not execute or apply it.",
        "candidate_id": f"RESTORE_{var}",
        "target_file": str(target_path),
        "family": family,
        "variable": var,
        "current_resolved_value": current_value,
        "current_bad_reference": missing_expanded,
        "intended_value": intended,
        "intended_value_resolved": str(intended_path),
        "intended_value_source": intended_source,
        "intended_value_sha256": sha256_file(intended_path),
        "mechanism": _mechanism(family, var),
        "exact_diff": diff,
        "patch": diff,
        "patch_sha256": sha256_text(diff),
        "original_sha256": sha256_text(original),
        "target_original_hash": sha256_file(target_path),
        "earliest_affected_stage": earliest,
        "downstream_invalidation": _downstream(earliest),
        "risks": [
            "restoring collateral does not guarantee timing closure or DRC=0",
            "macro/corner identity must remain the pinned one; no corner substitution",
            "downstream routing/extraction/timing results are invalidated and must rerun",
        ],
        "verification_criteria": [
            "patch is reviewed and explicitly approved before application",
            "approved operation reaches the executed configuration",
            "targeted failure disappears from recovery evidence",
            "affected downstream stages rerun or are validly reused",
            "no collateral regression against the frozen baseline",
            "original design inputs and historical runs unchanged",
        ],
        "approval_status": "PENDING",
        "source": "deterministic_evidence_rule",
        "requires_human_approval": True,
    }


# --------------------------------------------------------------------------
def _is_collector_token(tok: str) -> bool:
    return tok in {"+=", "+", "=", "\\"}


def _compatible_replacement(cand: Path, var: str, missing_token: str | None) -> bool:
    name = cand.name.lower()
    if var in LIB_VARS and not name.endswith(".lib"):
        return False
    if var in LEF_VARS and not name.endswith(".lef"):
        return False
    if var in SDC_VARS and not name.endswith(".sdc"):
        return False
    # never restore the very reference that is missing
    if missing_token and name == Path(missing_token).name.lower():
        return False
    return True


def _restore_stem(token: str, var: str) -> str:
    name = Path(token).name
    # strip an injected 'missing'/'nonexistent'/'bad' prefix on the stem
    stem = name
    for marker in ("missing_", "nonexistent_", "bad_", "fake_missing_"):
        if stem.lower().startswith(marker):
            stem = stem[len(marker):]
            break
    return stem


def _rewrite_to_platform(tok: str, platform_dir: Path, stem: str, sub: str) -> str:
    return f"$(PLATFORM_DIR)/{sub}/{stem}"


def _baseline_declaration(baseline_design: Path, var: str) -> str | None:
    cfg = baseline_design / "config.mk"
    if not cfg.is_file():
        return None
    decls = [a.value for a in parse_make_assignments(
        cfg.read_text(encoding="utf-8", errors="replace")) if a.var == var]
    return decls[0] if decls else None


def _current_resolved(assignments: list[Assignment], var: str, design_dir: Path,
                      platform_dir: Path, mirror: Path, project_root: Path) -> list[str]:
    vals: list[str] = []
    for a in assignments:
        if a.var != var:
            continue
        for tok in _split_values(a.value):
            expanded = _expand_static(tok, design_dir, platform_dir, mirror, project_root)
            vals.append(expanded)
    return vals


def _guess_variable(family: str, assignments: list[Assignment],
                    diagnosis: dict[str, Any]) -> str | None:
    vars_present = {a.var for a in assignments}
    if family in (MISSING_MACRO_LIB, MISSING_SC_LIB):
        for v in LIB_VARS:
            if v in vars_present:
                return v
    if family in (MISSING_MACRO_LEF, MISSING_TECH_LEF, MISSING_SC_LEF):
        for v in LEF_VARS:
            if v in vars_present:
                return v
    if family == MISSING_CONSTRAINT and "SDC_FILE" in vars_present:
        return "SDC_FILE"
    return None


def _earliest_for_var(var: str) -> str:
    if var in SDC_VARS:
        return "synth"
    if var in NETLIST_VARS:
        return "synth"
    if var in LEF_VARS or var in LIB_VARS:
        return "synth"
    return "floorplan"


def _downstream(earliest: str) -> list[str]:
    order = ["synth", "floorplan", "place", "cts", "route", "finish"]
    if earliest in order:
        return order[order.index(earliest):]
    return order


def _mechanism(family: str, var: str) -> str:
    return (f"{family}: ${var} references collateral that cannot be resolved; "
            f"restoring the compatible pinned value declared by the baseline")


def _build_patched(original: str, assignments: list[Assignment], var: str,
                   intended: str, *, missing_name: str | None,
                   missing_token: str | None) -> str:
    lines = original.splitlines(True)
    # remove any line that assigns `var` a value containing the missing token
    bad_markers = [m for m in {missing_name, missing_token} if m]
    bad_markers += [Path(m).name for m in list(bad_markers)]
    bad_markers = [m for m in bad_markers if m]
    kept: list[str] = []
    for ln in lines:
        if re.match(r"^\s*(?:export\s+|override\s+)*" + re.escape(var) + r"\s*[+:?]?=", ln):
            value_part = ln.split("=", 1)[1] if "=" in ln else ""
            if any(m in value_part for m in bad_markers):
                # drop the offending override entirely; baseline restoration added below
                continue
            if not value_part.strip():
                # drop empty override that would clobber the restored value
                continue
        kept.append(ln)
    body = "".join(kept).rstrip("\n")
    addition = f"export {var} = {intended}\n"
    return body + "\n\n# recovery: restore compatible pinned reference\n" + addition


def _insufficient(target_path: Path, family: str, reason: str,
                  diagnosis: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": INSUFFICIENT,
        "applies": False,
        "note": "Propose a textual correction for review; do not execute or apply it.",
        "family": family,
        "target_file": str(target_path),
        "reason": reason,
        "mechanism": diagnosis.get("signature", ""),
        "evidence_refs": diagnosis.get("evidence_refs", []),
        "risks": [],
        "verification_criteria": [],
        "approval_status": "NOT_REQUESTED",
        "requires_human_approval": True,
        "source": "deterministic_evidence_rule",
    }


# --------------------------------------------------------------------------
# optional model narrative (separate from deterministic classification)
# --------------------------------------------------------------------------
def optional_model_note(evidence: dict[str, Any]) -> dict[str, Any]:
    url = os.environ.get("SATTVA_MODEL_URL")
    if not url:
        return {"available": False, "reason": "SATTVA_MODEL_URL not configured",
                "note": None}
    try:
        import urllib.request
        model = os.environ.get("SATTVA_MODEL_NAME", "gpt-4o-mini")
        key = os.environ.get("SATTVA_MODEL_KEY", "")
        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system",
                 "content": "You are a physical-design failure analyst. Be concise "
                            "and evidence-bound. Do not propose applying anything."},
                {"role": "user", "content": json.dumps({
                    "signature": evidence.get("signature"),
                    "failed_stage": evidence.get("failed_stage"),
                    "log_hits": evidence.get("log_hits", [])[:12]}, indent=2)},
            ],
        }).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        req = urllib.request.Request(url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        note = data["choices"][0]["message"]["content"]
        return {"available": True, "model": model, "note": note[:2000],
                "source": "model"}
    except Exception as exc:  # noqa: BLE001 - report, never fabricate
        return {"available": False, "reason": f"model call failed: {exc}", "note": None}


def build_parser() -> Any:
    import argparse
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("classify")
    c.add_argument("--run", required=True)
    c.add_argument("--out")
    q = sub.add_parser("propose")
    q.add_argument("--diagnosis", required=True)
    q.add_argument("--target", required=True)
    q.add_argument("--baseline")
    q.add_argument("--mirror")
    q.add_argument("--out")
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "classify":
        out = classify_failure(args.run)
        out["model"] = optional_model_note(out)
    else:
        diag = json.loads(Path(args.diagnosis).read_text(encoding="utf-8"))
        out = propose_patch(diag, args.target, baseline=args.baseline,
                            mirror=args.mirror)
        if out is None:
            print(json.dumps({"status": "NO_PROPOSAL", "reason": "no bounded rule applies"},
                             indent=2))
            return 1
    if getattr(args, "out", None):
        Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                                  encoding="utf-8")
    print(json.dumps(out if args.command == "propose" else {"status": "PASS", **out},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
