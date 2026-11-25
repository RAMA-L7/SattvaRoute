#!/usr/bin/env python3
"""Bounded, advisory-only live diagnosis provider.

This module is intentionally separate from the verified deterministic path in
`diagnosis_agent.py`. It never executes EDA, never edits files other than its
own evidence artifacts, and never applies or approves a patch. A model response
is advisory text until a human approves an exact operation elsewhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
PROMPT_VERSION = "t1_diag_prompt/v1"
SCHEMA_VERSION = "t1_live_diagnosis/v1"

REQUIRED_FIELDS = (
    "failure_class", "failed_stage", "primary_hypothesis", "supporting_evidence",
    "contradicting_evidence", "alternative_hypotheses", "confidence",
    "proposed_action", "patch_candidate", "expected_effect", "affected_stages",
    "risk_assessment", "verification_plan", "missing_information",
)
REF_RE = re.compile(r"^E\d{2}$")
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{12,}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{10,}"),
    re.compile(r"(?i)authorization\s*[:=]\s*\S+"),
)


class DiagnosisError(Exception):
    """Raised on configuration or response problems that must not be guessed."""


@dataclass
class ModelConfig:
    url: str | None
    model: str
    key_present: bool
    provider: str = "openai-compatible"
    timeout_s: float = 30.0
    max_attempts: int = 1
    min_interval_s: float = 0.0
    temperature: float = 0.0
    max_tokens: int = 1200

    @classmethod
    def from_env(cls) -> "ModelConfig":
        def number(name: str, default: float, lo: float, hi: float) -> float:
            try:
                v = float(os.environ.get(name, default))
            except (TypeError, ValueError):
                return default
            return max(lo, min(hi, v))

        def integer(name: str, default: int, lo: int, hi: int) -> int:
            try:
                return max(lo, min(hi, int(os.environ.get(name, default))))
            except (TypeError, ValueError):
                return default

        key = os.environ.get("SATTVA_MODEL_KEY", "")
        return cls(
            url=os.environ.get("SATTVA_MODEL_URL") or None,
            model=os.environ.get("SATTVA_MODEL_NAME", "gpt-4o-mini"),
            key_present=bool(key.strip()),
            provider=os.environ.get("SATTVA_MODEL_PROVIDER", "openai-compatible"),
            timeout_s=number("SATTVA_MODEL_TIMEOUT_SECS", 30.0, 1.0, 120.0),
            max_attempts=integer("SATTVA_MODEL_MAX_ATTEMPTS", 1, 1, 3),
            min_interval_s=number("SATTVA_MODEL_MIN_INTERVAL_S", 0.0, 0.0, 5.0),
            temperature=number("SATTVA_MODEL_TEMPERATURE", 0.0, 0.0, 1.0),
            max_tokens=integer("SATTVA_MODEL_MAX_TOKENS", 1200, 64, 4096),
        )

    def fingerprint(self) -> str:
        data = {"provider": self.provider, "model": self.model,
                "timeout_s": self.timeout_s, "max_attempts": self.max_attempts,
                "min_interval_s": self.min_interval_s,
                "temperature": self.temperature, "max_tokens": self.max_tokens}
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def redact(text: str, key: str = "") -> str:
    out = text
    if key:
        out = out.replace(key, "[REDACTED_CREDENTIAL]")
    for pattern in SECRET_PATTERNS:
        out = pattern.sub("[REDACTED]", out)
    return out


def _default_transport(url: str, payload: bytes, headers: dict[str, str],
                       timeout_s: float) -> tuple[int, bytes, dict[str, str]]:
    req = urllib.request.Request(url, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.status, resp.read(), dict(resp.headers.items())


def validate_schema(obj: Any) -> list[str]:
    errors = []
    if not isinstance(obj, dict):
        return ["response is not a JSON object"]
    for field in REQUIRED_FIELDS:
        if field not in obj:
            errors.append(f"missing field: {field}")
    if not isinstance(obj.get("affected_stages"), list):
        errors.append("affected_stages must be a list")
    for field in ("supporting_evidence", "contradicting_evidence",
                  "alternative_hypotheses", "risk_assessment", "verification_plan",
                  "missing_information"):
        if field in obj and not isinstance(obj[field], list):
            errors.append(f"{field} must be a list")
    return errors


def validate_refs(obj: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    """Resolve E01..E06 references by id + verbatim excerpt + excerpt hash."""
    allowed = {e["id"]: e for e in bundle.get("entries", [])}
    results: list[dict[str, Any]] = []
    fabricated: list[str] = []
    cited: set[str] = set()

    def check(ref: Any, excerpt: Any) -> None:
        if not isinstance(ref, str) or not REF_RE.match(ref):
            fabricated.append(str(ref))
            results.append({"ref": ref, "status": "FABRICATED"})
            return
        cited.add(ref)
        entry = allowed.get(ref)
        if entry is None:
            fabricated.append(ref)
            results.append({"ref": ref, "status": "FABRICATED"})
            return
        if not isinstance(excerpt, str) or excerpt.strip() != entry["text"]:
            results.append({"ref": ref, "status": "EXCERPT_MISMATCH"})
            return
        digest = hashlib.sha256(excerpt.strip().encode()).hexdigest()
        status = "RESOLVED" if digest == entry["excerpt_sha256"] else "HASH_MISMATCH"
        results.append({"ref": ref, "status": status})

    # Check every evidence-bearing field, not just supporting_evidence.
    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "ref" in node:
                check(node.get("ref"), node.get("excerpt"))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(obj)
    return {"refs": results, "fabricated": fabricated,
            "distinct_valid": len({r["ref"] for r in results
                                   if r["status"] == "RESOLVED"}),
            "valid": not fabricated and all(r["status"] == "RESOLVED" for r in results)}


def call_model(prompt: str, bundle: dict[str, Any], config: ModelConfig | None = None,
               *, transport: Callable[..., tuple[int, bytes, dict[str, str]]] | None = None,
               sleep_fn: Callable[[float], None] = time.sleep,
               raw_out: str | Path | None = None,
               key: str = "") -> dict[str, Any]:
    """Perform one bounded, labelled model call. No execution authority."""
    cfg = config or ModelConfig.from_env()
    started = time.monotonic()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "status": "SKIPPED_NO_CREDENTIALS",
        "execution_kind": "stub" if transport is not None else "live_api_candidate",
        "provider": cfg.provider, "model_id": cfg.model,
        "config_sha256": cfg.fingerprint(), "prompt_version": PROMPT_VERSION,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "evidence_bundle_id": bundle.get("bundle_id"),
        "bundle_sha256": bundle.get("bundle_sha256"),
        "request_started_at": started_utc, "request_completed_at": None,
        "latency_ms": None, "retries": 0, "retry_reasons": [],
        "http_status": None, "token_usage": None, "raw_response_sha256": None,
        "schema_valid": False, "refs_valid": False, "parsed_output": None,
        "errors": [], "redactions": [], "idempotency_key": hashlib.sha256(
            (str(bundle.get("bundle_id")) + PROMPT_VERSION + cfg.model).encode()).hexdigest(),
        "credential_present": cfg.key_present,
    }
    if not cfg.url:
        record["execution_kind"] = "not_invoked"
        record["latency_ms"] = int((time.monotonic() - started) * 1000)
        record["request_completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return record
    if cfg.provider != "openai-compatible":
        record["status"] = "UNSUPPORTED_PROVIDER"
        record["errors"].append("only openai-compatible wire shape is supported")
        return record

    secret = key or os.environ.get("SATTVA_MODEL_KEY", "")
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["Authorization"] = f"Bearer {secret}"
        record["redactions"].append("Authorization header omitted from artifacts")
    payload = json.dumps({
        "model": cfg.model, "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}],
    }, sort_keys=True).encode("utf-8")
    fn = transport or _default_transport
    last_error = ""
    for attempt in range(1, cfg.max_attempts + 1):
        if cfg.min_interval_s and attempt > 1:
            sleep_fn(cfg.min_interval_s)
        try:
            status, body, resp_headers = fn(cfg.url, payload, headers, cfg.timeout_s)
            record["http_status"] = status
            raw = redact(body.decode("utf-8", errors="replace"), secret)
            record["raw_response_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
            if raw_out:
                Path(raw_out).parent.mkdir(parents=True, exist_ok=True)
                Path(raw_out).write_text(raw + "\n", encoding="utf-8")
            if status == 429:
                retry_after = resp_headers.get("Retry-After") or resp_headers.get("retry-after")
                try:
                    delay = min(float(retry_after), cfg.timeout_s)
                except (TypeError, ValueError):
                    delay = min(2.0 ** attempt, cfg.timeout_s)
                last_error = "rate_limited"
                if attempt < cfg.max_attempts:
                    record["retries"] += 1
                    record["retry_reasons"].append("rate_limited")
                    sleep_fn(delay)
                    continue
                record["status"] = "RATE_LIMITED"
                break
            if status >= 500:
                last_error = "http_error"
                if attempt < cfg.max_attempts:
                    record["retries"] += 1
                    record["retry_reasons"].append("http_5xx")
                    sleep_fn(min(2.0 ** attempt, cfg.timeout_s))
                    continue
                record["status"] = "HTTP_ERROR"
                break
            if status == 401 or status == 403:
                record["status"] = "AUTH_ERROR"
                break
            if status >= 400:
                record["status"] = "HTTP_ERROR"
                break
            data = json.loads(raw)
            content = data.get("choices", [ {} ])[0].get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                record["status"] = "MALFORMED_RESPONSE"
                break
            parsed = json.loads(content)
            errors = validate_schema(parsed)
            record["parsed_output"] = parsed
            record["schema_valid"] = not errors
            record["errors"].extend(errors)
            refs = validate_refs(parsed, bundle)
            record["refs_valid"] = refs["valid"]
            record["reference_validation"] = refs
            usage = data.get("usage")
            record["token_usage"] = usage if isinstance(usage, dict) else None
            record["status"] = "OK" if not errors and refs["valid"] else (
                "SCHEMA_INVALID" if errors else "REF_FABRICATION")
            break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = "timeout" if isinstance(exc, TimeoutError) else "transport_error"
            if attempt < cfg.max_attempts:
                record["retries"] += 1
                record["retry_reasons"].append(last_error)
                sleep_fn(min(2.0 ** attempt, cfg.timeout_s))
                continue
            record["status"] = "TIMEOUT" if last_error == "timeout" else "TRANSPORT_ERROR"
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            record["status"] = "MALFORMED_RESPONSE"
            record["errors"].append(type(exc).__name__)
    if last_error and not record["errors"]:
        record["errors"].append(redact(last_error, secret))
    record["latency_ms"] = int((time.monotonic() - started) * 1000)
    record["request_completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("config", help="print redacted provider configuration")
    c.set_defaults(func=lambda a: {"status": "PASS",
                                   "config": ModelConfig.from_env().fingerprint(),
                                   "url_set": bool(ModelConfig.from_env().url),
                                   "key_set": ModelConfig.from_env().key_present})
    r = sub.add_parser("call", help="make one bounded live call")
    r.add_argument("--bundle", required=True)
    r.add_argument("--prompt", required=True)
    r.add_argument("--raw-out")
    r.set_defaults(func=lambda a: call_model(
        Path(a.prompt).read_text(encoding="utf-8"),
        json.loads(Path(a.bundle).read_text(encoding="utf-8")),
        raw_out=a.raw_out))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    print(json.dumps(args.func(args), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
