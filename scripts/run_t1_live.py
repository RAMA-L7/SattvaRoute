#!/usr/bin/env python3
"""Execute one genuine T1 live diagnosis through the existing call_model path.

WSL cannot reach the Windows-loopback Ollama endpoint directly, so a narrow
PowerShell forwarder is used as the HTTP transport. The request/response is a
real provider call; no stub, replay, or fixture is involved.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
E = ROOT / "experiments" / "T1-LIVE-DIAG" / "T-PNR-001" / "v1"
OUT = ROOT / "experiments" / "T1-LIVE-DIAG" / "T-PNR-001" / "v1_live"
WIN_SCRIPT = r"D:\SattvaRoute\scripts\t1_ollama_forward.ps1"
WIN_BODY = r"C:\Users\91846\AppData\Local\Temp\opencode\t1live_body.json"
WIN_RESP = r"C:\Users\91846\AppData\Local\Temp\opencode\t1live_resp.json"
WSL_BODY = Path("/mnt/c/Users/91846/AppData/Local/Temp/opencode/t1live_body.json")
WSL_RESP = Path("/mnt/c/Users/91846/AppData/Local/Temp/opencode/t1live_resp.json")

sys.path.insert(0, str(ROOT / "scripts"))
from live_diagnosis import ModelConfig, call_model  # noqa: E402
from evaluate_diagnosis import grade  # noqa: E402


def ps_transport(url: str, payload: bytes, headers: dict[str, str],
                 timeout_s: float) -> tuple[int, bytes, dict[str, str]]:
    WSL_BODY.write_bytes(payload)
    if WSL_RESP.exists():
        WSL_RESP.unlink()
    cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", WIN_SCRIPT, "-BodyFile", WIN_BODY, "-OutFile", WIN_RESP,
           "-Endpoint", url, "-TimeoutSec", str(max(1, int(timeout_s)))]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s + 30)
    if proc.returncode != 0 or not WSL_RESP.exists():
        raise OSError(f"forwarder failed rc={proc.returncode}: {proc.stderr[-200:]}")
    data = json.loads(WSL_RESP.read_text(encoding="utf-8-sig"))
    return int(data["status"]), str(data["body"]).encode("utf-8"), {}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grade-only", action="store_true",
                        help="regrade the existing live_call.json without a new provider call")
    args = parser.parse_args()
    bundle = json.loads((E / "bundle.json").read_text(encoding="utf-8"))
    prompt = (E / "prompt.txt").read_text(encoding="utf-8")
    gt = json.loads((E / "gt.json").read_text(encoding="utf-8"))
    if args.grade_only:
        call = json.loads((OUT / "live_call.json").read_text(encoding="utf-8"))
        if call.get("parsed_output") is not None:
            from live_diagnosis import validate_refs
            refs = validate_refs(call["parsed_output"], bundle)
            call["reference_validation"] = refs
            call["refs_valid"] = refs["valid"]
            (OUT / "live_call.json").write_text(
                json.dumps(call, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if call.get("parsed_output") is None:
            print(json.dumps({"status": "NOT_RUN", "reason": "no parsed output to grade"}))
            return 1
        evaluation = grade(call["parsed_output"], bundle, gt)
        evaluation["call_status"] = call["status"]
        evaluation["score_semantics"] = ("diagnostic_only" if not evaluation["diagnosis_accepted"]
                                         else "accepted")
        (OUT / "live_eval.json").write_text(
            json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PASS", "graded": True,
                          "diagnosis_accepted": evaluation["diagnosis_accepted"],
                          "hard_gates": evaluation["hard_gates"],
                          "scores": evaluation["scores"]}, indent=2, sort_keys=True))
        return 0
    cfg = ModelConfig(
        url="http://127.0.0.1:11434/v1/chat/completions",
        model=os.environ.get("SATTVA_MODEL_NAME", "qwen2.5:7b-instruct"),
        key_present=False, provider="openai-compatible",
        timeout_s=300.0, max_attempts=1, min_interval_s=0.0,
        temperature=0.0, max_tokens=900)
    OUT.mkdir(parents=True, exist_ok=True)
    call = call_model(prompt, bundle, cfg, transport=ps_transport,
                      live_transport=True, raw_out=OUT / "raw_response.txt")
    (OUT / "live_call.json").write_text(json.dumps(call, indent=2, sort_keys=True) + "\n",
                                        encoding="utf-8")
    result: dict[str, Any] = {"status": call["status"],
                              "execution_kind": call["execution_kind"],
                              "provider": "ollama-local", "model_id": cfg.model,
                              "endpoint": cfg.url, "http_status": call["http_status"],
                              "latency_ms": call["latency_ms"],
                              "retries": call["retries"],
                              "token_usage": call["token_usage"],
                              "schema_valid": call["schema_valid"],
                              "refs_valid": call["refs_valid"],
                              "errors": call["errors"]}
    if call.get("parsed_output") is not None:
        (OUT / "live_output.json").write_text(
            json.dumps(call["parsed_output"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        evaluation = grade(call["parsed_output"], bundle, gt)
        evaluation["call_status"] = call["status"]
        evaluation["score_semantics"] = ("diagnostic_only" if not evaluation["diagnosis_accepted"]
                                         else "accepted")
        (OUT / "live_eval.json").write_text(
            json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["evaluation"] = evaluation
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if call["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
