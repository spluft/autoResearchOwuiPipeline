"""decisions-shim: Open WebUI /decisions (OpenAI predicate dialect) -> 9router /v1/systemone (noul dialect).

OWUI (tool_permissions.py review_with_decisions) POSTs {model, input, questions:[{type:'predicate',
name, instructions}]} and requires {"answers":[{"name","type":"predicate","probability"}]} with
probability in [0,1]. Anything malformed / non-200 makes OWUI fail closed to a human, so this shim
never fabricates a low probability: every upstream failure is a 502.
ND's /v1/decisions accepts the SAME systemone body, so SHIM_UPSTREAM_URL can be pointed straight
at https://api.neuraldeep.ru/v1/decisions (plan-B) without code changes.
"""
import json
import os
import time

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

UPSTREAM_URL = os.environ.get("SHIM_UPSTREAM_URL", "http://192.168.1.200:30613/v1/systemone")
UPSTREAM_KEY = os.environ.get("SHIM_UPSTREAM_KEY", "")
MODEL = os.environ.get("SHIM_MODEL", "oc/jev-1.13-free")
UPSTREAM_TIMEOUT = float(os.environ.get("SHIM_UPSTREAM_TIMEOUT", "4.0"))
MAX_STATE = int(os.environ.get("SHIM_MAX_STATE", "60000"))

app = FastAPI()


def audit(rec: dict) -> None:
    rec["ts"] = round(time.time(), 3)
    print(json.dumps(rec, ensure_ascii=False), flush=True)


async def call_upstream(payload: dict) -> tuple[int, dict | None, str]:
    """Return (status, json_or_None, error_name). Isolated for tests."""
    try:
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT) as client:
            r = await client.post(
                UPSTREAM_URL,
                json=payload,
                headers={"Authorization": f"Bearer {UPSTREAM_KEY}",
                         "Content-Type": "application/json"},
            )
        if r.status_code != 200:
            return r.status_code, None, f"http_{r.status_code}"
        return 200, r.json(), ""
    except Exception as exc:  # timeouts, connect errors, bad json
        return 0, None, type(exc).__name__


@app.get("/healthz")
async def healthz():
    return {"ok": True, "model": MODEL, "upstream": UPSTREAM_URL}


@app.post("/decisions")
async def decisions(request: Request):
    t0 = time.perf_counter()
    ms = lambda: round((time.perf_counter() - t0) * 1000)
    try:
        body = await request.json()
        evidence = body["input"]
        questions = body["questions"]
        assert isinstance(evidence, str) and evidence
        assert isinstance(questions, list) and 1 <= len(questions) <= 16
    except Exception:
        audit({"event": "bad_request", "ms": ms()})
        return JSONResponse({"error": "invalid OWUI decisions payload"}, status_code=400)

    q_map: dict[str, dict] = {}
    for q in questions:
        if (not isinstance(q, dict) or q.get("type") != "predicate"
                or not isinstance(q.get("name"), str) or not q["name"] or q["name"] in q_map):
            return JSONResponse({"error": "unsupported question"}, status_code=400)
        q_map[q["name"]] = {"type": "noul",
                            "instructions": str(q.get("instructions", ""))[:8000]}

    payload = {"model": MODEL, "state": evidence[:MAX_STATE], "questions": q_map}
    status, up, err = await call_upstream(payload)
    if status != 200 or up is None:
        audit({"event": "upstream_error", "err": err, "status": status, "ms": ms()})
        return JSONResponse({"error": "upstream unavailable"}, status_code=502)

    answers = up.get("answers")
    if not isinstance(answers, dict):
        audit({"event": "upstream_bad_json", "ms": ms()})
        return JSONResponse({"error": "upstream answers missing"}, status_code=502)

    out = []
    for name in q_map:
        a = answers.get(name)
        prob = a.get("noul") if isinstance(a, dict) else None
        if not isinstance(prob, (int, float)) or isinstance(prob, bool) \
                or not 0.0 <= prob <= 1.0:
            audit({"event": "upstream_bad_answer", "name": name, "ms": ms()})
            return JSONResponse({"error": "upstream answer invalid"}, status_code=502)
        out.append({"name": name, "type": "predicate", "probability": float(prob)})

    audit({"event": "verdict", "model": MODEL, "probability": out[0]["probability"],
           "n_questions": len(out), "evidence_bytes": len(evidence), "ms": ms()})
    return {"answers": out}
