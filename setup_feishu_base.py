#!/usr/bin/env python3
"""Owner helper: bind an existing Feishu Base, keep its review table, and create the experience table."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
SCRIPT_DIR = ROOT / "skills" / "fortior-knowledge-contributor" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import bootstrap_feishu as bf  # noqa: E402
from common import (  # noqa: E402
    feishu_tenant_access_token,
    load_config,
    require,
    update_config_values,
)


def parse_base_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    match = re.search(r"/base/([^/?#]+)", parsed.path)
    if not match:
        raise RuntimeError("Unable to parse Feishu Base app_token from URL")
    app_token = match.group(1)
    table_id = (parse_qs(parsed.query).get("table") or [""])[0].strip()
    if not table_id:
        raise RuntimeError("URL does not contain ?table=tbl... for the existing review-point table")
    return app_token, table_id


def ensure_fields_resumable(app_token: str, table_id: str, token: str, fields: list[dict]) -> None:
    """Add missing fields and recover safely when Feishu times out after accepting a request."""
    existing = {x.get("field_name") for x in bf.list_fields(app_token, table_id, token)}
    for spec in fields:
        fname = spec["field_name"]
        if fname in existing:
            print(f"  exists: {fname}")
            continue
        try:
            bf.create_field(app_token, table_id, token, spec)
            existing.add(fname)
            print(f"  added: {fname}")
            continue
        except Exception as first_exc:
            print(f"  warning: create field {fname} returned an error: {first_exc}")

        # A write may have succeeded even when the client timed out waiting for the response.
        refreshed = {x.get("field_name") for x in bf.list_fields(app_token, table_id, token)}
        if fname in refreshed:
            existing = refreshed
            print(f"  recovered: {fname} already exists after the timeout")
            continue

        print(f"  retrying once: {fname}")
        bf.create_field(app_token, table_id, token, spec)
        existing.add(fname)
        print(f"  added after retry: {fname}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bind an existing Feishu Base and create/extend only the Engineering Experience table"
    )
    parser.add_argument("--base-url", required=True, help="Feishu Base URL whose current table is the existing review-point table")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    parsed_input = urlparse(args.base_url)
    base_host = parsed_input.netloc or "fcntoutafc56.feishu.cn"
    app_token, review_table_id = parse_base_url(args.base_url)

    # Persist non-secret routing first. App ID/Secret must already exist locally.
    update_config_values({
        "FEISHU_APP_TOKEN": app_token,
        "FEISHU_REVIEW_POINT_TABLE_ID": review_table_id,
        "FEISHU_EXPERIENCE_TABLE_NAME": "工程经验贡献",
    })

    cfg = load_config()
    require(cfg, "FEISHU_APP_ID", "FEISHU_APP_SECRET")
    token = feishu_tenant_access_token(cfg)

    tables = bf.list_tables(app_token, token)
    review_table = next((x for x in tables if x.get("table_id") == review_table_id), None)
    if not review_table:
        raise RuntimeError(f"Existing review-point table is not accessible in this Base: {review_table_id}")

    print(f"Bound Base: {app_token}")
    print(f"Existing review-point table: {review_table.get('name', '')} -> {review_table_id}")
    print("Review-point table is READ ONLY during this setup; no fields will be modified.")

    review_fields = bf.list_fields(app_token, review_table_id, token)
    print("\nExisting review-point fields:")
    for item in review_fields:
        print(f"  - {item.get('field_name')} | type={item.get('type')} | id={item.get('field_id', '')}")

    exp_name = cfg.get("FEISHU_EXPERIENCE_TABLE_NAME", "工程经验贡献")
    exp_configured_id = cfg.get("FEISHU_EXPERIENCE_TABLE_ID", "").strip()
    exp_id = bf.resolve_table(
        app_token,
        token,
        exp_name,
        exp_configured_id,
        bf.EXPERIENCE_FIELDS[0],
        args.dry_run,
    )

    if args.dry_run:
        if exp_id:
            existing = {x.get("field_name") for x in bf.list_fields(app_token, exp_id, token)}
            for spec in bf.EXPERIENCE_FIELDS:
                if spec["field_name"] not in existing:
                    print(f"  would add: {spec['field_name']}")
        print("\nDRY RUN: no Feishu table/field changes were made.")
        return

    if not exp_id:
        raise RuntimeError("Experience table was not resolved/created")

    # Save the table ID immediately. A later field timeout must not lose routing state.
    path = update_config_values({
        "FEISHU_APP_TOKEN": app_token,
        "FEISHU_REVIEW_POINT_TABLE_ID": review_table_id,
        "FEISHU_EXPERIENCE_TABLE_ID": exp_id,
        "FEISHU_EXPERIENCE_TABLE_NAME": exp_name,
    })
    print(f"Saved experience table routing before field migration: {exp_id}")

    ensure_fields_resumable(app_token, exp_id, token, bf.EXPERIENCE_FIELDS)

    # Re-list tables after all writes so the final success message is backed by a fresh read.
    final_tables = bf.list_tables(app_token, token)
    if not any(x.get("table_id") == exp_id for x in final_tables):
        raise RuntimeError(f"Experience table disappeared from Base after setup: {exp_id}")

    review_url = f"https://{base_host}/base/{app_token}?table={review_table_id}"
    experience_url = f"https://{base_host}/base/{app_token}?table={exp_id}"

    print("\nFeishu routing ready:")
    print(f"  review_point -> {review_table_id}")
    print(f"  engineering_experience -> {exp_id}")
    print(f"Saved to: {path}")
    print("\nDirect table URLs (use these if the Feishu sidebar has not refreshed yet):")
    print(f"  review_point: {review_url}")
    print(f"  engineering_experience: {experience_url}")
    print("Next: test an experience submission, then test the existing review-point table adapter.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
