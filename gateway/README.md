# Fortior Contribution Gateway — Open MVP

This reference service accepts contributions without account login. It supports two sinks:

- `mock`: local JSONL file for safe end-to-end testing;
- `feishu`: real Feishu/Lark Bitable write.

## Recommended first run: mock mode

Install dependencies:

```bash
python -m pip install -r gateway/requirements.txt
```

Windows PowerShell:

```powershell
$env:FORTIOR_GATEWAY_MODE="open"
$env:FORTIOR_GATEWAY_SINK="mock"
python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8080
```

macOS/Linux:

```bash
export FORTIOR_GATEWAY_MODE=open
export FORTIOR_GATEWAY_SINK=mock
python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8080
```

Health check:

```bash
curl http://127.0.0.1:8080/health
```

Expected:

```json
{"ok":true,"mode":"open","sink":"mock"}
```

Mock submissions are written to:

```text
gateway/mock-submissions.jsonl
```

This file is gitignored.

## Automatic mock integration test

```bash
python gateway/test_gateway.py
```

Expected:

```text
Gateway mock tests: PASS
```

The test verifies:

- health endpoint;
- account-free submission;
- mock record creation;
- duplicate suppression;
- required contributor username validation.

## Real Feishu mode

Only after mock testing passes, configure server-side credentials:

```env
FORTIOR_GATEWAY_MODE=open
FORTIOR_GATEWAY_SINK=feishu

FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_APP_TOKEN=...
FEISHU_EXPERIENCE_TABLE_ID=...
FEISHU_REVIEW_POINT_TABLE_ID=...
```

Then:

```bash
python -m uvicorn gateway.app:app --host 0.0.0.0 --port 8080
```

Client endpoint:

```text
POST /v1/contributions
```

Normal contributors never receive the Feishu App Secret; it exists only on the Gateway server.

## Optional edit-code mode

Later, without requiring any account system:

```env
FORTIOR_GATEWAY_MODE=edit_code
FORTIOR_GATEWAY_EDIT_CODE=change-me
```

Clients add:

```text
X-Fortior-Edit-Code: change-me
```

Open mode remains the MVP default.

## Limitations

The MVP keeps rate-limit and duplicate state in memory. This is enough for functional validation and a single-process reference deployment. A production multi-instance deployment should move counters and idempotency state to a shared durable store.

See the repository root `TESTING.md` for the complete Skill → Gateway → Feishu test procedure.
