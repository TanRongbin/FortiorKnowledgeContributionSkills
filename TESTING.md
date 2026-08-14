# Maintainer Testing Guide

> 本文档面向仓库维护者 / Owner。普通贡献者请使用 [CONTRIBUTOR_QUICKSTART.md](CONTRIBUTOR_QUICKSTART.md)，不需要运行 mock Gateway、配置飞书或执行建表脚本。

维护测试分为四层。按层排查可以快速判断问题发生在本地结构化、Gateway、飞书还是 Agent Skill 执行层。

## Layer 1 — 本地 Schema / 提交脚本

无需 Gateway、无需飞书：

```bash
python submit.py --type experience --file skills/fortior-knowledge-contributor/examples/experience-example.json --dry-run
python submit.py --type review_point --file skills/fortior-knowledge-contributor/examples/review-point-example.json --dry-run
```

预期：

```text
Validation: PASS
Submission: DRY RUN
```

如果这里失败，问题在 payload / Schema / 本地提交脚本，与公网网络和飞书无关。

也可以运行本地 smoke test：

```bash
python -m pip install -r gateway/requirements.txt
python quick_test.py
```

## Layer 2 — Gateway Mock

Mock 会真正走 HTTP，但不会访问飞书。

### 启动

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

检查：

```bash
curl http://127.0.0.1:8080/health
```

预期至少包含：

```json
{"ok":true,"mode":"open","sink":"mock"}
```

自动集成测试：

```bash
python gateway/test_gateway.py
```

预期：

```text
Gateway mock tests: PASS
```

Mock 记录位于 `gateway/mock-submissions.jsonl`，该文件已 gitignore。需要查看时可运行：

```bash
python view_mock.py --last 5
```

## Layer 3 — 飞书与托管 Gateway

### 3.1 Owner 本地飞书配置

真实飞书凭据只放在 Owner 本地配置或托管 Gateway 的 Secret 环境变量中，永远不要提交到 GitHub：

```text
~/.fortior/knowledge-contributor.env
```

需要：

```env
FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_APP_TOKEN=...
FEISHU_EXPERIENCE_TABLE_ID=...
FEISHU_REVIEW_POINT_TABLE_ID=...
```

### 3.2 现有 Review Point 表 + 新 Engineering Experience 表

当前生产结构是 **同一个 Feishu Base 内两张表**：

```text
现有 Review Point 表         保留其已有字段和语义
工程经验贡献表               由本仓库创建/补齐
```

如果已有 Review Point 表，使用：

```bash
python setup_feishu_base.py --base-url "https://<tenant>.feishu.cn/base/<app_token>?table=<existing_review_table_id>"
```

这个脚本会把现有 Review Point 表作为只读路由目标，只创建或补齐 `工程经验贡献` 表。

**不要**为了当前生产 Base 对现有 Review Point 表运行 generic `bootstrap_feishu.py --only review_point`。generic bootstrap 只适合全新、隔离的测试 Base 或未来明确批准的迁移场景。

需要查看真实字段时：

```bash
python inspect_feishu.py --table-id <table_id>
```

### 3.3 Owner 直写验证

仅维护者可以临时使用：

```text
FORTIOR_SUBMIT_MODE=feishu_direct
```

然后分别运行：

```bash
python submit.py --type experience --file skills/fortior-knowledge-contributor/examples/experience-example.json
python submit.py --type review_point --file skills/fortior-knowledge-contributor/examples/review-point-example.json
```

两条都必须出现：

```text
Validation: PASS
Submission: PASS
```

并分别进入对应飞书表。

### 3.4 托管公网 Gateway

当前公开入口：

```text
https://fortior-knowledge-contribution-gateway.onrender.com
```

进程健康检查：

```bash
curl https://fortior-knowledge-contribution-gateway.onrender.com/health
```

预期包含：

```json
{"ok":true,"mode":"open","sink":"feishu","version":"<current>"}
```

其中 `version` 应与当前部署代码一致，不要求文档写死具体版本号。

飞书 readiness：

```bash
curl https://fortior-knowledge-contribution-gateway.onrender.com/ready
```

真正可提交时必须包含：

```json
{"ok":true,"sink":"feishu","stage":"ready","version":"<current>"}
```

如果 `/health` 正常而 `/ready` 失败，按返回的 `stage` 排查：

```text
config              缺少托管环境变量
auth                App ID / App Secret 无法认证
experience_table    工程经验表不可访问
review_point_table  评审点表不可访问
```

### 3.5 多人写入

Gateway 对同一目标表使用进程内写锁，并对飞书瞬时网络错误、`1254290` 和 `1254291` 做退避重试。当前 Render Free 是单实例方案；如果未来扩展到多实例，需要把排队、限流和幂等状态迁移到共享持久化存储。

## Layer 4 — 真实 Agent Skill 验收

安装最新版本：

```bash
python install.py --target all
```

彻底关闭并重启 AI CLI，然后在真实工程会话中测试：

```text
把刚刚解决的问题同时总结成工程经验和可复用评审点并分别贡献。
```

验收点：

1. Skill 能读取当前上下文和真实工程证据，不要求重复描述已有内容；
2. 宿主支持结构化问答时，必答项以单选/多选交互出现；
3. 用户明确选择用户名、署名、可见范围和披露边界；
4. AI 展示提交预览；
5. Windows 沙箱环境下能定位真实用户目录中的稳定 runtime；
6. payload 通过临时 JSON 文件提交，不使用超长 here-document；
7. Experience 和 Review Point 分别调用 runtime；
8. 两条都返回真实远程结果：

```text
Validation: PASS
Submission: PASS
sink: feishu
record_id: rec...
```

9. 飞书两张目标表分别出现对应记录；
10. `Submission: PASS` 只解释为进入待治理数据，不宣称已成为正式规则。

## CI

GitHub Actions `.github/workflows/validate.yml` 当前负责：

- Python 编译检查；
- 两种示例 payload dry-run；
- Review Point → 飞书字段映射回归；
- stable runtime 安装/执行；
- Gateway mock 集成测试。

CI 不持有生产飞书 Secret，因此不会在 GitHub Actions 中写生产飞书。
