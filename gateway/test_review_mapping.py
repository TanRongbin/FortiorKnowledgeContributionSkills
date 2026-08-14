#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "fortior-knowledge-contributor" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from submit import review_fields  # noqa: E402


def main() -> None:
    payload = json.loads(
        (ROOT / "skills" / "fortior-knowledge-contributor" / "examples" / "review-point-example.json")
        .read_text(encoding="utf-8")
    )
    meta = {
        "submission_id": "test-submission",
        "content_hash": "test-hash",
        "client_version": "test-version",
    }
    fields = review_fields(payload, meta)

    expected = {
        "问题标题": "外部长度字段参与接收计数前的边界约束",
        "问题类别": "通信协议",
        "工程系列": ["通用嵌入式"],
        "项目/产品": "示例通信固件",
        "程序模块": ["UART/Communication"],
        "运行阶段": ["运行时", "接收中断/状态机"],
        "根因确认程度": "已确认",
        "证据类型": ["源码审查", "测试/复现"],
        "不适用情况": "协议长度由编译期常量固定且不存在外部可控长度输入",
        "敏感信息状态": "无敏感信息",
    }
    for key, value in expected.items():
        actual = fields.get(key)
        if actual != value:
            raise AssertionError(f"{key}: expected {value!r}, got {actual!r}")

    for preserved in [
        "背景说明", "异常表现", "触发条件", "根本原因/机理", "影响",
        "涉及符号/代码", "证据说明", "修复方式", "验证方式", "评审问题",
        "检查方法", "失败判据", "备注",
    ]:
        if preserved not in fields:
            raise AssertionError(f"preserved mapping missing: {preserved}")

    print("Review point Feishu mapping: PASS")


if __name__ == "__main__":
    main()
