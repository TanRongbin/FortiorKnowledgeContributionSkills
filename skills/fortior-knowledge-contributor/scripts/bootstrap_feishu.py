#!/usr/bin/env python3
"""Create or non-destructively extend the two Fortior contribution tables."""
from __future__ import annotations

import argparse
import sys

from common import feishu_tenant_access_token, http_json, load_config, require

TEXT = 1
NUMBER = 2
SINGLE = 3
CHECKBOX = 7


def select(name: str, options: list[str]) -> dict:
    return {"field_name": name, "type": SINGLE, "property": {"options": [{"name": x} for x in options]}}


def text(name: str) -> dict:
    return {"field_name": name, "type": TEXT}


def checkbox(name: str) -> dict:
    return {"field_name": name, "type": CHECKBOX}


def number(name: str) -> dict:
    return {"field_name": name, "type": NUMBER}


COMMON_FIELDS = [
    text("提交ID"),
    # Client-declared identity: useful for attribution, never sufficient for abuse controls.
    text("贡献者用户名"), text("显示名"), text("GitHub用户名"),
    # Server-verified identity: written by the production Contribution Gateway.
    text("身份提供方"), text("已验证用户名"), text("已验证用户ID"),
    select("身份验证状态", ["未验证", "客户端声明", "服务端已验证", "Owner直写"]),
    select("公开范围", ["公开", "匿名公开", "仅治理人员可见"]),
    select("公开署名方式", ["用户名", "显示名", "匿名"]),
    checkbox("允许公开仓库名"), checkbox("允许公开Commit"), checkbox("允许公开文件路径"), checkbox("允许公开代码摘录"),
    checkbox("权利确认"), text("仓库"), text("分支"), text("Commit"), text("相关文件"), text("证据"),
    text("内容哈希"), text("客户端版本"),
    select("风控状态", ["客户端预检", "clean", "suspected_spam", "blocked"]), number("风控分"),
    select("治理状态", ["待治理", "治理中", "需补充", "已采纳", "已拒绝", "重复"]), text("原始JSON"),
]

EXPERIENCE_FIELDS = [
    text("经验标题"), text("简要摘要"), text("领域"), text("问题背景"), text("问题描述"), text("问题现象"),
    text("触发条件"), text("定位过程"), text("根因"),
    select("根因可信度", ["confirmed", "strong_hypothesis", "unconfirmed"]),
    text("解决方案"), text("代码/参数变更"), text("验证方法"), text("验证结果"),
    select("验证状态", ["passed", "partial", "not_verified"]), text("收益"), text("经验教训"), text("适用范围"),
] + COMMON_FIELDS

REVIEW_FIELDS = [
    text("评审点标题"), text("简要摘要"), text("领域"), text("评审问题"), text("检查方法"), text("失败判据"),
    text("触发条件"), text("失败现象"), text("根因"), text("风险影响"), text("正确实践"), text("修复建议"),
    text("验证方法"), text("适用范围"), text("来源经验ID"),
] + COMMON_FIELDS


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def list_tables(app_token: str, token: str) -> list[dict]:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables?page_size=100"
    data = http_json("GET", url, headers=auth(token))
    if data.get("code") != 0:
        raise RuntimeError(f"List tables failed: {data}")
    return data.get("data", {}).get("items", [])


def create_table(app_token: str, token: str, name: str, primary_field: dict) -> str:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
    body = {"table": {"name": name, "default_view_name": "全部记录", "fields": [primary_field]}}
    data = http_json("POST", url, body, auth(token))
    if data.get("code") != 0:
        raise RuntimeError(f"Create table {name} failed: {data}")
    info = data.get("data", {})
    table_id = info.get("table_id") or (info.get("table") or {}).get("table_id")
    if not table_id:
        raise RuntimeError(f"No table_id in response: {data}")
    return table_id


def list_fields(app_token: str, table_id: str, token: str) -> list[dict]:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields?page_size=100"
    data = http_json("GET", url, headers=auth(token))
    if data.get("code") != 0:
        raise RuntimeError(f"List fields failed: {data}")
    return data.get("data", {}).get("items", [])


def create_field(app_token: str, table_id: str, token: str, spec: dict) -> None:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    data = http_json("POST", url, spec, auth(token))
    if data.get("code") != 0:
        raise RuntimeError(f"Create field {spec['field_name']} failed: {data}")


def ensure_table(app_token: str, token: str, name: str, fields: list[dict], dry_run: bool) -> str | None:
    tables = list_tables(app_token, token)
    found = next((x for x in tables if x.get("name") == name), None)
    if found:
        table_id = found["table_id"]
        print(f"Found table: {name} -> {table_id}")
    elif dry_run:
        print(f"Would create table: {name}")
        return None
    else:
        table_id = create_table(app_token, token, name, fields[0])
        print(f"Created table: {name} -> {table_id}")

    existing = {x.get("field_name"): x for x in list_fields(app_token, table_id, token)}
    for spec in fields:
        fname = spec["field_name"]
        if fname in existing:
            # Non-destructive by design: do not rewrite existing field options/types.
            continue
        if dry_run:
            print(f"  would add: {fname}")
        else:
            create_field(app_token, table_id, token, spec)
            print(f"  added: {fname}")
    return table_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = load_config()
    require(cfg, "FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_APP_TOKEN")
    token = feishu_tenant_access_token(cfg)
    app_token = cfg["FEISHU_APP_TOKEN"]
    exp_name = cfg.get("FEISHU_EXPERIENCE_TABLE_NAME", "工程经验贡献")
    rp_name = cfg.get("FEISHU_REVIEW_POINT_TABLE_NAME", "评审点贡献")

    exp_id = ensure_table(app_token, token, exp_name, EXPERIENCE_FIELDS, args.dry_run)
    rp_id = ensure_table(app_token, token, rp_name, REVIEW_FIELDS, args.dry_run)

    if not args.dry_run:
        print("\nWrite these values into ~/.fortior/knowledge-contributor.env:")
        print(f"FEISHU_EXPERIENCE_TABLE_ID={exp_id}")
        print(f"FEISHU_REVIEW_POINT_TABLE_ID={rp_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
