#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from pathlib import Path

from common import compact, feishu_tenant_access_token, http_json, load_config, require

CLIENT_VERSION = "0.3.3"
MAX_PAYLOAD_BYTES = 128 * 1024
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b"),
]

VISIBILITY_LABEL = {
    "public": "公开",
    "anonymized_public": "匿名公开",
    "private_governance_only": "仅治理人员可见",
}
ATTRIBUTION_LABEL = {"username": "用户名", "display_name": "显示名", "anonymous": "匿名"}
ROOT_CAUSE_CONFIDENCE_LABEL = {
    "confirmed": "已确认",
    "strong_hypothesis": "强假设",
    "unconfirmed": "未确认",
}
SENSITIVE_STATUS_LABEL = {
    "no_sensitive_info": "无敏感信息",
    "sanitized": "已脱敏",
    "restricted": "受限/仅治理可见",
}


def validate(payload: dict, kind: str) -> list[str]:
    warnings: list[str] = []
    expected = "engineering_experience" if kind == "experience" else "review_point"
    if payload.get("contribution_type") != expected:
        raise RuntimeError(f"contribution_type must be {expected}")
    if payload.get("schema_version") != "1.0":
        raise RuntimeError("schema_version must be 1.0")
    if not str(payload.get("title", "")).strip():
        raise RuntimeError("title is required")

    contributor = payload.get("contributor") or {}
    if not str(contributor.get("username", "")).strip():
        raise RuntimeError("contributor.username is required")

    prefs = payload.get("submission_preferences") or {}
    required_prefs = [
        "visibility", "attribution", "allow_repository_name", "allow_commit_id",
        "allow_file_paths", "allow_code_excerpt", "rights_confirmed",
    ]
    missing = [k for k in required_prefs if k not in prefs]
    if missing:
        raise RuntimeError("Mandatory pre-submit answers are missing: " + ", ".join(missing))
    if prefs.get("visibility") not in VISIBILITY_LABEL:
        raise RuntimeError("Invalid submission_preferences.visibility")
    if prefs.get("attribution") not in ATTRIBUTION_LABEL:
        raise RuntimeError("Invalid submission_preferences.attribution")
    if prefs.get("rights_confirmed") is not True:
        raise RuntimeError("rights_confirmed must be explicitly true")

    privacy = payload.get("privacy") or {}
    if privacy.get("contains_private_code") and not privacy.get("sanitized"):
        raise RuntimeError("Private code is present but payload is not marked sanitized")

    raw = json.dumps(payload, ensure_ascii=False)
    size = len(raw.encode("utf-8"))
    if size > MAX_PAYLOAD_BYTES:
        raise RuntimeError(f"Payload too large: {size} bytes > {MAX_PAYLOAD_BYTES}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(raw):
            raise RuntimeError("High-confidence credential/private-key pattern detected")

    if len(str(payload.get("summary", "")).strip()) < 12:
        warnings.append("summary is very short")
    if not payload.get("evidence_items"):
        warnings.append("no evidence_items supplied")

    if kind == "review_point":
        completion_keys = [
            "problem_category", "engineering_series", "project_product", "chip_models",
            "cpu_architectures", "program_modules", "runtime_stages", "root_cause_confidence",
            "evidence_types", "non_applicable_conditions",
        ]
        if not any(payload.get(key) for key in completion_keys):
            warnings.append("review-point engineering context is sparse; run the field-completion pass before production submission")
    return warnings


def canonical_hash(payload: dict) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def metadata(payload: dict, cfg: dict[str, str]) -> dict:
    return {
        "submission_id": str(uuid.uuid4()),
        "content_hash": canonical_hash(payload),
        "client_version": cfg.get("FORTIOR_CLIENT_VERSION", CLIENT_VERSION),
        "client_instance_id": cfg.get("FORTIOR_CLIENT_INSTANCE_ID", ""),
        "identity_status": "未验证",
        "identity_provider": "",
        "verified_username": "",
        "verified_user_id": "",
    }


def text_list(value) -> str:
    if isinstance(value, list):
        return "\n".join(str(v) for v in value)
    return compact(value)


def string_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def common_feishu_fields(payload: dict, meta: dict) -> dict:
    contributor = payload.get("contributor", {})
    prefs = payload.get("submission_preferences", {})
    source = payload.get("source", {})
    return {
        "提交ID": meta.get("submission_id", ""),
        "贡献者用户名": contributor.get("username", ""),
        "显示名": contributor.get("display_name", ""),
        "GitHub用户名": contributor.get("github_username", ""),
        "客户端实例ID": meta.get("client_instance_id", ""),
        "身份提供方": meta.get("identity_provider", ""),
        "已验证用户名": meta.get("verified_username", ""),
        "已验证用户ID": meta.get("verified_user_id", ""),
        "身份验证状态": meta.get("identity_status", "未验证"),
        "公开范围": VISIBILITY_LABEL[prefs["visibility"]],
        "公开署名方式": ATTRIBUTION_LABEL[prefs["attribution"]],
        "允许公开仓库名": bool(prefs["allow_repository_name"]),
        "允许公开Commit": bool(prefs["allow_commit_id"]),
        "允许公开文件路径": bool(prefs["allow_file_paths"]),
        "允许公开代码摘录": bool(prefs["allow_code_excerpt"]),
        "权利确认": bool(prefs["rights_confirmed"]),
        "仓库": source.get("repository", ""),
        "分支": source.get("branch", ""),
        "Commit": source.get("commit", ""),
        "相关文件": text_list(source.get("files", [])),
        "证据": text_list(payload.get("evidence_items", [])),
        "内容哈希": meta.get("content_hash", ""),
        "客户端版本": meta.get("client_version", CLIENT_VERSION),
        "风控状态": meta.get("risk_status", "客户端预检"),
        "风控分": meta.get("risk_score", 0),
        "治理状态": "待治理",
        "原始JSON": json.dumps(payload, ensure_ascii=False),
    }


def experience_fields(payload: dict, meta: dict) -> dict:
    root = payload.get("root_cause", {})
    verification = payload.get("verification", {})
    fields = {
        "经验标题": payload.get("title", ""),
        "简要摘要": payload.get("summary", ""),
        "领域": text_list(payload.get("domain", [])),
        "问题背景": payload.get("problem_context", ""),
        "问题描述": payload.get("problem_description", ""),
        "问题现象": payload.get("symptom", ""),
        "触发条件": text_list(payload.get("trigger_conditions", [])),
        "定位过程": text_list(payload.get("investigation_process", [])),
        "根因": root.get("description", ""),
        "根因可信度": root.get("status", ""),
        "解决方案": payload.get("solution", ""),
        "代码/参数变更": text_list(payload.get("code_or_parameter_changes", [])),
        "验证方法": verification.get("method", ""),
        "验证结果": verification.get("result", ""),
        "验证状态": verification.get("status", ""),
        "收益": payload.get("benefit", ""),
        "经验教训": text_list(payload.get("lessons_learned", [])),
        "适用范围": text_list(payload.get("applicable_scope", [])),
    }
    fields.update(common_feishu_fields(payload, meta))
    return fields


def _review_disclosed_source(payload: dict) -> str:
    source = payload.get("source") or {}
    prefs = payload.get("submission_preferences") or {}
    parts: list[str] = []
    if prefs.get("allow_repository_name") and source.get("repository"):
        parts.append(f"仓库: {source['repository']}")
    if source.get("branch"):
        parts.append(f"分支: {source['branch']}")
    if prefs.get("allow_commit_id") and source.get("commit"):
        parts.append(f"Commit: {source['commit']}")
    if prefs.get("allow_file_paths") and source.get("files"):
        parts.append("文件:\n" + text_list(source.get("files", [])))
    if prefs.get("allow_code_excerpt") and payload.get("code_symbols"):
        parts.append("涉及符号:\n" + text_list(payload.get("code_symbols", [])))
    return "\n".join(parts)


def _review_project_product(payload: dict) -> str:
    explicit = str(payload.get("project_product", "")).strip()
    if explicit:
        return explicit
    prefs = payload.get("submission_preferences") or {}
    repository = str((payload.get("source") or {}).get("repository", "")).strip()
    if prefs.get("allow_repository_name") and repository:
        return repository.rstrip("/").split("/")[-1]
    return ""


def _infer_review_evidence_types(payload: dict) -> list[str]:
    explicit = string_list(payload.get("evidence_types"))
    if explicit:
        return explicit

    result: list[str] = []
    source = payload.get("source") or {}
    prefs = payload.get("submission_preferences") or {}
    evidence_text = "\n".join(string_list(payload.get("evidence_items"))).lower()

    if prefs.get("allow_file_paths") and source.get("files"):
        result.append("源码/文件")
    if prefs.get("allow_commit_id") and source.get("commit"):
        result.append("Git提交")
    if any(word in evidence_text for word in ["log", "日志"]):
        result.append("日志")
    if any(word in evidence_text for word in ["waveform", "波形", "曲线", "trace", "抓波"]):
        result.append("波形/Trace")
    if any(word in evidence_text for word in ["test", "测试", "复现", "验证"]):
        result.append("测试/复现")
    if any(word in evidence_text for word in ["datasheet", "document", "文档", "规范", "手册"]):
        result.append("工程文档")
    if payload.get("evidence_items") and not result:
        result.append("工程证据")
    return list(dict.fromkeys(result))


def _review_sensitive_status(payload: dict) -> str:
    explicit = str(payload.get("sensitive_information_status", "")).strip()
    if explicit in SENSITIVE_STATUS_LABEL:
        return SENSITIVE_STATUS_LABEL[explicit]

    privacy = payload.get("privacy") or {}
    prefs = payload.get("submission_preferences") or {}
    if prefs.get("visibility") == "private_governance_only":
        return SENSITIVE_STATUS_LABEL["restricted"]
    if privacy.get("contains_private_code") or privacy.get("sanitized"):
        return SENSITIVE_STATUS_LABEL["sanitized"]
    return SENSITIVE_STATUS_LABEL["no_sensitive_info"]


def review_fields(payload: dict, meta: dict) -> dict:
    """Map the public Review Point schema into the existing Fortior Feishu review table.

    Existing mapped content is preserved. Optional engineering-context fields are added when
    available; absent context is omitted instead of guessed. Feishu accepts option names for
    single/multi-select fields and creates missing options when necessary.
    """
    contributor = payload.get("contributor") or {}
    prefs = payload.get("submission_preferences") or {}
    source_experience_ids = text_list(payload.get("source_experience_ids", []))
    correct = text_list(payload.get("correct_practice", []))
    fix = text_list(payload.get("fix_recommendation", []))
    fix_text = "\n".join(x for x in [correct, fix] if x)

    context_note_pairs = [
        ("问题类别", payload.get("problem_category")),
        ("工程系列", text_list(payload.get("engineering_series", []))),
        ("项目/产品", _review_project_product(payload)),
        ("芯片型号", text_list(payload.get("chip_models", []))),
        ("CPU架构", text_list(payload.get("cpu_architectures", []))),
        ("程序模块", text_list(payload.get("program_modules", []))),
        ("运行阶段", text_list(payload.get("runtime_stages", []))),
        ("根因确认程度", ROOT_CAUSE_CONFIDENCE_LABEL.get(str(payload.get("root_cause_confidence", "")), "")),
        ("证据类型", text_list(_infer_review_evidence_types(payload))),
        ("不适用情况", text_list(payload.get("non_applicable_conditions", []))),
    ]

    notes = [
        f"简要摘要: {payload.get('summary', '')}",
        f"领域: {text_list(payload.get('domain', []))}",
        f"适用范围: {text_list(payload.get('applicable_scope', []))}",
        f"来源经验ID: {source_experience_ids}",
        f"贡献者用户名: {contributor.get('username', '')}",
        f"公开范围: {VISIBILITY_LABEL[prefs['visibility']]}",
        f"公开署名方式: {ATTRIBUTION_LABEL[prefs['attribution']]}",
        f"提交ID: {meta.get('submission_id', '')}",
        f"内容哈希: {meta.get('content_hash', '')}",
        f"客户端版本: {meta.get('client_version', CLIENT_VERSION)}",
    ]
    notes.extend(f"{label}: {value}" for label, value in context_note_pairs if value)
    notes = [x for x in notes if not x.endswith(": ")]

    fields = {
        "问题标题": payload.get("title", ""),
        "责任人": contributor.get("username", ""),
        "背景说明": payload.get("summary", ""),
        "异常表现": text_list(payload.get("failure_symptoms", [])),
        "触发条件": text_list(payload.get("trigger_conditions", [])),
        "根本原因/机理": payload.get("root_cause", ""),
        "影响": text_list(payload.get("risk_impact", [])),
        "涉及符号/代码": _review_disclosed_source(payload),
        "证据说明": text_list(payload.get("evidence_items", [])),
        "修复方式": fix_text,
        "验证方式": text_list(payload.get("verification_method", [])),
        "不适用情况": text_list(payload.get("non_applicable_conditions", [])),
        "评审问题": payload.get("review_question", ""),
        "检查方法": text_list(payload.get("inspection_method", [])),
        "失败判据": text_list(payload.get("failure_criteria", [])),
        "敏感信息状态": _review_sensitive_status(payload),
        "备注": "\n".join(notes),
    }

    problem_category = str(payload.get("problem_category", "")).strip()
    if problem_category:
        fields["问题类别"] = problem_category

    engineering_series = string_list(payload.get("engineering_series"))
    if engineering_series:
        fields["工程系列"] = engineering_series

    project_product = _review_project_product(payload)
    if project_product:
        fields["项目/产品"] = project_product

    chip_models = string_list(payload.get("chip_models"))
    if chip_models:
        fields["芯片型号"] = "\n".join(chip_models)

    cpu_architectures = string_list(payload.get("cpu_architectures"))
    if cpu_architectures:
        fields["CPU架构"] = cpu_architectures

    program_modules = string_list(payload.get("program_modules"))
    if program_modules:
        fields["程序模块"] = program_modules

    runtime_stages = string_list(payload.get("runtime_stages"))
    if runtime_stages:
        fields["运行阶段"] = runtime_stages

    root_confidence = ROOT_CAUSE_CONFIDENCE_LABEL.get(str(payload.get("root_cause_confidence", "")), "")
    if root_confidence:
        fields["根因确认程度"] = root_confidence

    evidence_types = _infer_review_evidence_types(payload)
    if evidence_types:
        fields["证据类型"] = evidence_types

    return fields


def submit_gateway(cfg: dict[str, str], kind: str, payload: dict, meta: dict):
    require(cfg, "FORTIOR_CONTRIBUTION_ENDPOINT")
    headers = {"X-Fortior-Client-Version": meta.get("client_version", CLIENT_VERSION)}
    if cfg.get("FORTIOR_CONTRIBUTION_EDIT_CODE"):
        headers["X-Fortior-Edit-Code"] = cfg["FORTIOR_CONTRIBUTION_EDIT_CODE"]
    return http_json(
        "POST",
        cfg["FORTIOR_CONTRIBUTION_ENDPOINT"].rstrip("/") + "/v1/contributions",
        {"type": kind, "payload": payload, "client_metadata": meta},
        headers,
    )


def submit_feishu_direct(cfg: dict[str, str], kind: str, payload: dict, meta: dict):
    require(cfg, "FEISHU_APP_TOKEN")
    table_key = "FEISHU_EXPERIENCE_TABLE_ID" if kind == "experience" else "FEISHU_REVIEW_POINT_TABLE_ID"
    require(cfg, table_key)
    direct_meta = dict(meta)
    direct_meta["identity_status"] = "Owner直写"
    token = feishu_tenant_access_token(cfg)
    fields = experience_fields(payload, direct_meta) if kind == "experience" else review_fields(payload, direct_meta)
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{cfg['FEISHU_APP_TOKEN']}/tables/{cfg[table_key]}/records"
    result = http_json("POST", url, {"fields": fields}, {"Authorization": f"Bearer {token}"})
    if result.get("code") != 0:
        raise RuntimeError(f"Feishu create record failed: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["experience", "review_point"], required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = json.loads(Path(args.file).read_text(encoding="utf-8-sig"))
    cfg = load_config()
    warnings = validate(payload, args.type)
    meta = metadata(payload, cfg)
    print(f"Validation: PASS | content_hash={meta['content_hash']}")
    for warning in warnings:
        print(f"Warning: {warning}")

    if args.dry_run:
        print("Submission: DRY RUN")
        return

    mode = cfg.get("FORTIOR_SUBMIT_MODE", "local_only")
    if mode == "local_only":
        print("Submission: local_only; no remote write performed")
        return
    if mode == "gateway":
        result = submit_gateway(cfg, args.type, payload, meta)
    elif mode == "feishu_direct":
        result = submit_feishu_direct(cfg, args.type, payload, meta)
    else:
        raise RuntimeError(f"Unknown FORTIOR_SUBMIT_MODE: {mode}")

    print("Submission: PASS")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
