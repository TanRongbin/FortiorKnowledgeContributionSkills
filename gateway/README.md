# Fortior Contribution Gateway

This directory contains the public HTTP submission service used by `fortior-knowledge-contributor`.

普通贡献者不需要运行这里的任何命令。默认公共入口已经由安装器配置：

```text
https://fortior-knowledge-contribution-gateway.onrender.com
```

本文件面向 Gateway 维护者。

## Endpoints

```text
GET  /health
GET  /ready
POST /v1/contributions
```

### `/health`

只检查 Gateway 进程和当前运行模式：

```json
{"ok":true,"mode":"open","sink":"feishu","version":"<current>"}
```

### `/ready`

当 `sink=feishu` 时还会真实检查：

- Feishu App ID / App Secret 能否获取 tenant access token；
- Engineering Experience 目标表是否可访问；
- Review Point 目标表是否可访问。

正常生产状态：

```json
{"ok":true,"sink":"feishu","stage":"ready","version":"<current>"}
```

`version` 应与当前部署代码一致。如果失败，`stage` 会指出 `config`、`auth`、`experience_table` 或 `review_point_table`。

## Sinks

Gateway 支持：

```text
mock    本地 JSONL，供开发/集成测试
feishu  真实写入 Feishu/Lark Bitable
```

托管公共 Gateway 使用 `feishu`。

## Local mock development

安装依赖：

```bash
python -m pip install -r gateway/requirements.txt
```

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
python gateway/test_gateway.py
```

Mock 记录写入 `gateway/mock-submissions.jsonl`，该文件已 gitignore。

## Real Feishu mode

服务端环境变量：

```env
FORTIOR_GATEWAY_MODE=open
FORTIOR_GATEWAY_SINK=feishu

FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_APP_TOKEN=...
FEISHU_EXPERIENCE_TABLE_ID=...
FEISHU_REVIEW_POINT_TABLE_ID=...
```

不要把这些 Secret 提交到 GitHub。普通贡献者也不需要获得这些值。

本地维护者运行：

```bash
python -m uvicorn gateway.app:app --host 0.0.0.0 --port 8080
```

## Hosted Render service

仓库根目录的 `render.yaml` 定义当前 Render Web Service。生产配置使用：

```text
plan: free
FORTIOR_GATEWAY_MODE=open
FORTIOR_GATEWAY_SINK=feishu
healthCheckPath: /health
```

飞书相关变量使用 Render Secret 环境变量，不写入 Blueprint 明文。

更新 `main` 后 Render 应按 Blueprint 配置自动部署最新 commit。需要排障时先看：

```text
/health
/ready
Render deploy commit
Render environment variables
```

## Current concurrency behavior

当前 Gateway 是单进程设计：

- Experience 和 Review Point 两张表分别有进程内写锁；
- 同一目标表的写入在本进程内串行；
- 飞书瞬时网络错误、`1254290`、`1254291` 会做有限退避重试。

如果未来扩到多个 Gateway 实例，进程内锁不再足够，需要共享队列 / 分布式锁以及持久化幂等存储。

## Rate limit and dedupe

当前限流和短期去重状态保存在内存中。适合当前单实例、小规模贡献测试，但服务重启后状态会丢失。

普通贡献者不应该依赖这些机制作为永久业务去重；正式治理层仍需要 stable identity / version / content semantics。

## Optional edit-code mode

如需在不强制账号登录的前提下限制贡献入口：

```env
FORTIOR_GATEWAY_MODE=edit_code
FORTIOR_GATEWAY_EDIT_CODE=change-me
```

客户端需携带：

```text
X-Fortior-Edit-Code: change-me
```

## Tests

```bash
python gateway/test_gateway.py
python gateway/test_review_mapping.py
```

完整维护验收流程见仓库根目录 [TESTING.md](../TESTING.md)。
