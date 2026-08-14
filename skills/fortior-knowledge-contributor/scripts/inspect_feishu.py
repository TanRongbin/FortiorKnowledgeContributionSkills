#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from common import feishu_tenant_access_token, http_json, load_config, require


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def get_tables(app_token: str, token: str) -> list[dict]:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables?page_size=100"
    data = http_json("GET", url, headers=auth(token))
    if data.get("code") != 0:
        raise RuntimeError(f"List tables failed: {data}")
    return data.get("data", {}).get("items", [])


def get_fields(app_token: str, table_id: str, token: str) -> list[dict]:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields?page_size=100"
    data = http_json("GET", url, headers=auth(token))
    if data.get("code") != 0:
        raise RuntimeError(f"List fields failed for {table_id}: {data}")
    return data.get("data", {}).get("items", [])


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only inspection of configured Feishu Bitable tables and fields")
    parser.add_argument("--table-id", help="Inspect one specific table id; otherwise list configured/contribution tables")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    cfg = load_config()
    require(cfg, "FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_APP_TOKEN")
    token = feishu_tenant_access_token(cfg)
    app_token = cfg["FEISHU_APP_TOKEN"]
    tables = get_tables(app_token, token)

    if args.table_id:
        target_ids = [args.table_id]
    else:
        configured = [
            cfg.get("FEISHU_REVIEW_POINT_TABLE_ID", "").strip(),
            cfg.get("FEISHU_EXPERIENCE_TABLE_ID", "").strip(),
        ]
        target_ids = [x for x in configured if x]
        if not target_ids:
            target_ids = [x.get("table_id", "") for x in tables if x.get("table_id")]

    out = []
    by_id = {x.get("table_id"): x for x in tables}
    for table_id in target_ids:
        info = by_id.get(table_id, {})
        fields = get_fields(app_token, table_id, token)
        out.append({
            "table_id": table_id,
            "table_name": info.get("name", ""),
            "fields": [
                {
                    "field_id": f.get("field_id", ""),
                    "field_name": f.get("field_name", ""),
                    "type": f.get("type"),
                    "is_primary": bool(f.get("is_primary")),
                }
                for f in fields
            ],
        })

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    for item in out:
        print(f"Table: {item['table_name'] or '(unknown)'} -> {item['table_id']}")
        for f in item["fields"]:
            primary = " primary" if f["is_primary"] else ""
            print(f"  - {f['field_name']} | type={f['type']} | id={f['field_id']}{primary}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
