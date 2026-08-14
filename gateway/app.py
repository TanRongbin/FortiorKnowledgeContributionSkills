from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "fortior-knowledge-contributor" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from common import feishu_tenant_access_token, http_json  # noqa: E402
from submit import experience_fields, review_fields  # noqa: E402

app = FastAPI(title="Fortior Contribution Gateway", version="0.2.0")

MAX_BYTES = int(os.environ.get("FORTIOR_GATEWAY_MAX_BYTES", str(128 * 1024)))
RATE_PER_HOUR = int(os.environ.get("FORTIOR_GATEWAY_RATE_LIMIT_PER_HOUR", "30"))
MODE = os.environ.get("FORTIOR_GATEWAY_MODE", "open").strip().lower()
EDIT_CODE = os.environ.get("FORTIOR_GATEWAY_EDIT_CODE", "")
SINK = os.environ.get("FORTIOR_GATEWAY_SINK", "mock").strip().lower()
MOCK_LOG = Path(
    os.environ.get(
        "FORTIOR_GATEWAY_MOCK_LOG",
        str(ROOT / "gateway" / "mock-submissions.jsonl"),
    )
)

RATE_BUCKETS: dict[str, deque[float]] = defaultdict(deque)
SEEN_HASHES: dict[str, float] = {}
DEDUPE_TTL = 24 * 3600


def cfg() -> dict[str, str]:
    return dict(os.environ)


def canonical_hash(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def enforce_mode(edit_code: str | None) -> None:
    if MODE == "open":
        return
    if MODE == "edit_code":
        if not EDIT_CODE:
            raise HTTPException(503, "Gateway edit-code mode is not configured")
        if edit_code != EDIT_CODE:
            raise HTTPException(403, "Contribution edit code required")
        return
    raise HTTPException(503, "Unsupported gateway mode")


def enforce_rate(key: str) -> None:
    now = time.time()
    bucket = RATE_BUCKETS[key]
    while bucket and bucket[0] < now - 3600:
        bucket.popleft()
    if len(bucket) >= RATE_PER_HOUR:
        raise HTTPException(429, "Contribution rate limit exceeded")
    bucket.append(now)


def cleanup_seen() -> None:
    now = time.time()
    for key, ts in list(SEEN_HASHES.items()):
        if ts < now - DEDUPE_TTL:
            del SEEN_HASHES[key]


def validate_payload(kind: str, payload: dict) -> None:
    expected = "engineering_experience" if kind == "experience" else "review_point"
    if kind not in {"experience", "review_point"}:
        raise HTTPException(400, "Unknown contribution type")
    if payload.get("contribution_type") != expected:
        raise HTTPException(400, "contribution_type mismatch")
    username = str((payload.get("contributor") or {}).get("username", "")).strip()
    if not username:
        raise HTTPException(400, "contributor.username is required")
    prefs = payload.get("submission_preferences") or {}
    required = [
        "visibility", "attribution", "allow_repository_name", "allow_commit_id",
        "allow_file_paths", "allow_code_excerpt", "rights_confirmed",
    ]
    if any(k not in prefs for k in required) or prefs.get("rights_confirmed") is not True:
        raise HTTPException(400, "Mandatory submission preferences are incomplete")


def write_feishu(kind: str, payload: dict, meta: dict) -> dict:
    conf = cfg()
    required = ["FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_APP_TOKEN"]
    table_key = "FEISHU_EXPERIENCE_TABLE_ID" if kind == "experience" else "FEISHU_REVIEW_POINT_TABLE_ID"
    required.append(table_key)
    missing = [k for k in required if not conf.get(k)]
    if missing:
        raise HTTPException(503, "Gateway Feishu configuration incomplete: " + ", ".join(missing))

    token = feishu_tenant_access_token(conf)
    fields = experience_fields(payload, meta) if kind == "experience" else review_fields(payload, meta)
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{conf['FEISHU_APP_TOKEN']}/tables/{conf[table_key]}/records"
    result = http_json("POST", url, {"fields": fields}, {"Authorization": f"Bearer {token}"})
    if result.get("code") != 0:
        raise HTTPException(502, f"Feishu create record failed: {result.get('msg', 'unknown')}")
    return result


def write_mock(kind: str, payload: dict, meta: dict) -> dict:
    MOCK_LOG.parent.mkdir(parents=True, exist_ok=True)
    record_id = "mock-" + meta["submission_id"]
    row = {
        "record_id": record_id,
        "received_at": int(time.time()),
        "type": kind,
        "payload": payload,
        "metadata": meta,
    }
    with MOCK_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"code": 0, "data": {"record": {"record_id": record_id}}}


def write_sink(kind: str, payload: dict, meta: dict) -> dict:
    if SINK == "mock":
        return write_mock(kind, payload, meta)
    if SINK == "feishu":
        return write_feishu(kind, payload, meta)
    raise HTTPException(503, "Unsupported gateway sink; use mock or feishu")


@app.get("/health")
def health():
    return {"ok": True, "mode": MODE, "sink": SINK}


@app.post("/v1/contributions")
async def contribute(request: Request, x_fortior_edit_code: str | None = Header(default=None)):
    enforce_mode(x_fortior_edit_code)

    raw = await request.body()
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "Payload too large")
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON")

    kind = body.get("type")
    payload = body.get("payload")
    client_meta = body.get("client_metadata") or {}
    if not isinstance(payload, dict):
        raise HTTPException(400, "payload must be an object")
    validate_payload(kind, payload)

    username = str(payload["contributor"]["username"]).strip().lower()
    instance_id = str(client_meta.get("client_instance_id", "")).strip()
    ip = request.client.host if request.client else "unknown"
    enforce_rate(f"ip:{ip}")
    enforce_rate(f"user:{username}")
    if instance_id:
        enforce_rate(f"instance:{instance_id}")

    cleanup_seen()
    content_hash = canonical_hash(payload)
    if content_hash in SEEN_HASHES:
        return {"ok": True, "duplicate": True, "content_hash": content_hash}

    meta = {
        "submission_id": str(uuid.uuid4()),
        "content_hash": content_hash,
        "client_version": str(client_meta.get("client_version", "unknown")),
        "client_instance_id": instance_id,
        "identity_status": "未验证",
        "identity_provider": "",
        "verified_username": "",
        "verified_user_id": "",
        "risk_status": "客户端预检",
        "risk_score": 0,
    }

    result = write_sink(kind, payload, meta)
    SEEN_HASHES[content_hash] = time.time()
    record = ((result.get("data") or {}).get("record") or {})
    return {
        "ok": True,
        "duplicate": False,
        "sink": SINK,
        "submission_id": meta["submission_id"],
        "content_hash": content_hash,
        "record_id": record.get("record_id"),
    }
