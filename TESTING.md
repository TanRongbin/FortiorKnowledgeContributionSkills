# Testing Guide

本仓库把测试分成三层。建议严格按顺序执行，这样出错时能快速定位是哪一层。

## Layer 1 — Skill / JSON 本地校验

无需 Gateway、无需飞书。

```bash
python submit.py --type experience --file skills/fortior-knowledge-contributor/examples/experience-example.json --dry-run
python submit.py --type review_point --file skills/fortior-knowledge-contributor/examples/review-point-example.json --dry-run
```

预期：

```text
Validation: PASS
Submission: DRY RUN
```

如果这里失败，问题在 Schema/字段/本地提交脚本，与网络和飞书无关。

## Layer 2 — Gateway Mock 全链路

这一层会真正走 HTTP，但不会访问飞书。贡献会写入本机 `gateway/mock-submissions.jsonl`。

### 2.1 安装依赖

```bash
python -m pip install -r gateway/requirements.txt
```

### 2.2 启动 Mock Gateway

Windows PowerShell：

```powershell
$env:FORTIOR_GATEWAY_MODE="open"
$env:FORTIOR_GATEWAY_SINK="mock"
python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8080
```

macOS/Linux：

```bash
export FORTIOR_GATEWAY_MODE=open
export FORTIOR_GATEWAY_SINK=mock
python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8080
```

另开终端：

```bash
curl http://127.0.0.1:8080/health
```

预期：

```json
{"ok":true,"mode":"open","sink":"mock"}
```

### 2.3 配置 Skill 走 Gateway

编辑：

```text
~/.fortior/knowledge-contributor.env
```

Windows 通常是：

```text
C:\Users\<用户名>\.fortior\knowledge-contributor.env
```

写入：

```env
FORTIOR_SUBMIT_MODE=gateway
FORTIOR_CONTRIBUTION_ENDPOINT=http://127.0.0.1:8080
```

### 2.4 提交示例经验

```bash
python submit.py --type experience --file skills/fortior-knowledge-contributor/examples/experience-example.json
```

预期包含：

```text
Submission: PASS
"record_id": "mock-..."
```

然后查看：

```text
gateway/mock-submissions.jsonl
```

应该出现一行完整贡献。

再次执行完全相同命令，预期：

```json
"duplicate": true
```

用于验证去重。

### 2.5 自动测试 Gateway

```bash
python gateway/test_gateway.py
```

预期：

```text
Gateway mock tests: PASS
```

## Layer 3 — 真实飞书

只有 Layer 1、2 都通过后再做。

### 3.1 准备飞书应用

需要一个你自己控制的飞书自建应用，并给它多维表格所需的读取/写入权限，同时确保该应用能够访问目标多维表格。

不要把 App Secret 写入 GitHub。

### 3.2 配置 Owner 本地环境

在 `~/.fortior/knowledge-contributor.env` 中填写：

```env
FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_APP_TOKEN=...
FEISHU_EXPERIENCE_TABLE_NAME=工程经验贡献
FEISHU_REVIEW_POINT_TABLE_NAME=评审点贡献
```

### 3.3 初始化/补齐飞书表

```bash
python bootstrap_feishu.py
```

脚本会非破坏性地：

- 复用已有的 `工程经验贡献` / `评审点贡献`；
- 缺表则创建；
- 已有字段不删不改；
- 缺失字段自动增加；
- 最后输出两个 `table_id`。

把输出填回本地配置：

```env
FEISHU_EXPERIENCE_TABLE_ID=tbl...
FEISHU_REVIEW_POINT_TABLE_ID=tbl...
```

### 3.4 先测试 Owner 直写

临时设置：

```env
FORTIOR_SUBMIT_MODE=feishu_direct
```

执行：

```bash
python submit.py --type experience --file skills/fortior-knowledge-contributor/examples/experience-example.json
```

然后在飞书 `工程经验贡献` 表里确认新增一行。

再测试：

```bash
python submit.py --type review_point --file skills/fortior-knowledge-contributor/examples/review-point-example.json
```

确认 `评审点贡献` 新增一行。

### 3.5 最终测试 Gateway → 飞书

Gateway 终端设置：

```env
FORTIOR_GATEWAY_MODE=open
FORTIOR_GATEWAY_SINK=feishu
FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_APP_TOKEN=...
FEISHU_EXPERIENCE_TABLE_ID=tbl...
FEISHU_REVIEW_POINT_TABLE_ID=tbl...
```

启动：

```bash
python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8080
```

客户端配置：

```env
FORTIOR_SUBMIT_MODE=gateway
FORTIOR_CONTRIBUTION_ENDPOINT=http://127.0.0.1:8080
```

再次执行经验提交。此时应通过 Gateway 写入真实飞书。

## Layer 4 — 真实 Skill 交互测试

完成安装：

```bash
python install.py --target auto
```

重新启动你的 AI CLI。在一个真实工程中解决一个小问题后，对 AI 说：

```text
把刚刚解决的问题贡献为工程经验
```

预期流程：

1. AI 利用当前上下文和 git diff 总结问题；
2. AI 给出拟定标题；
3. AI 询问用户名；
4. AI 询问公开/匿名公开/仅治理可见；
5. AI 询问是否公开仓库、Commit、文件路径、代码摘录；
6. AI 要求权利/敏感信息确认；
7. AI 展示最终预览；
8. 用户确认后提交；
9. AI 返回 submission_id / record_id。

建议第一次真实测试选择：

```text
用户名：Terry-Test
公开范围：仅治理人员可见
署名：用户名
仓库名：不公开
Commit：不公开
文件路径：不公开
代码摘录：不公开
权利确认：确认
```

这样即使测试记录进入飞书，也不会被误当成准备公开的知识。

## 最小验收标准

一条 Experience 测试至少应验证：

- 用户名出现在飞书；
- 标题正确；
- 问题/根因/方案/验证结果正确；
- 公开范围正确；
- 四个公开权限布尔值正确；
- 治理状态为 `待治理`；
- 内容哈希存在；
- 相同内容重复提交不会重复写入；
- 不要求 GitHub / 飞书登录。
