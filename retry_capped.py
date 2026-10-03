#!/usr/bin/env python3
"""Retry only incomplete capped responses using pilot.py's larger cap."""
import json
import uuid
from pathlib import Path

import pilot

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results.jsonl"


def main() -> int:
    records = [json.loads(line) for line in RESULTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    latest = {}
    for record in records:
        for model_result in record.get("models", []):
            latest[(record["case_id"], model_result["model"])] = model_result
    cases = {case["id"]: case for case in pilot.load_cases()}
    pending = []
    for (case_id, model), result in latest.items():
        tokens = result.get("completion_tokens") or 0
        answer = result.get("answer", "")
        old_cap = result.get("requested_max_tokens", 1200) < 3600
        incomplete = result.get("finish_reason") == "length" or not str(answer).strip()
        if old_cap and incomplete:
            pending.append((case_id, model))
    if not pending:
        print("No hay respuestas incompletas que necesiten ampliación.")
        return 0
    print(f"Se repetirán {len(pending)} pares caso/modelo con límite de 3,600 tokens; Jev y respuestas completas no se repetirán.")
    api_key = pilot.load_api_key()
    run_id = "cap3600-" + uuid.uuid4().hex[:8]
    with RESULTS.open("a", encoding="utf-8") as out:
        for case_id, model in pending:
            record = {"run_id": run_id, "retry_of": case_id, "case_id": case_id, "track": cases[case_id]["track"], "models": []}
            try:
                result = pilot.call_model(cases[case_id], model, api_key)
                record["models"].append(result)
                status = "respuesta" if result["answer"].strip() else "respuesta vacía"
                print(f"{case_id} {model}: {status}, {result['completion_tokens']} tokens, finish={result['finish_reason']}")
            except Exception as exc:
                record["models"].append({"model": model, "error": str(exc), "requested_max_tokens": 3600})
                print(f"{case_id} {model}: error ({exc})")
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
