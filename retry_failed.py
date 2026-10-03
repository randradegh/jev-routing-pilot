#!/usr/bin/env python3
"""Retry only failed model calls in results.jsonl; does not repeat Jev or successes."""
import json
import uuid
from pathlib import Path

import pilot

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results.jsonl"


def main() -> int:
    rows = [json.loads(line) for line in RESULTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    cases = {case["id"]: case for case in pilot.load_cases()}
    pending = []
    for record in rows:
        for model_result in record.get("models", []):
            if "error" in model_result:
                pending.append((record["case_id"], model_result["model"], model_result["error"]))
    if not pending:
        print("No hay fallos para reintentar.")
        return 0
    print(f"Se reintentarán {len(pending)} solicitudes fallidas, sin repetir Jev ni respuestas exitosas.")
    api_key = pilot.load_api_key()
    retry_id = "retry-" + uuid.uuid4().hex[:8]
    with RESULTS.open("a", encoding="utf-8") as out:
        for case_id, model, original_error in pending:
            entry = {"run_id": retry_id, "retry_of": case_id, "case_id": case_id, "track": cases[case_id]["track"], "models": []}
            try:
                answer = pilot.call_model(cases[case_id], model, api_key)
                entry["models"].append(answer)
                print(f"{case_id} {model}: reintento exitoso")
            except Exception as exc:
                entry["models"].append({"model": model, "error": str(exc), "previous_error": original_error})
                print(f"{case_id} {model}: reintento falló ({exc})")
            out.write(json.dumps(entry, ensure_ascii=False) + "\n")
            out.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
