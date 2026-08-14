# Fortior Contribution Gateway — Open MVP

This reference service accepts contributions without account login and writes them to Feishu Bitable using server-side credentials.

## Run

Set environment variables:

```env
FORTIOR_GATEWAY_MODE=open
FORTIOR_GATEWAY_RATE_LIMIT_PER_HOUR=30

FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_APP_TOKEN=...
FEISHU_EXPERIENCE_TABLE_ID=...
FEISHU_REVIEW_POINT_TABLE_ID=...
```

Then:

```bash
pip install -r gateway/requirements.txt
uvicorn gateway.app:app --host 0.0.0.0 --port 8080
```

Client endpoint:

```text
POST /v1/contributions
```

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

Open mode is intentionally the default MVP.

## Limitations

The reference implementation keeps rate-limit and dedupe state in memory. This is enough for functional validation and a single-instance MVP, but a production multi-instance deployment should move these counters to a shared store.
