# Submission Security & Anti-Spam

## Goal

Fortior 的 V1 贡献入口首先保证：**任何安装 Skill 的用户都可以贡献，而不要求 GitHub、飞书或企业账号登录。**

公开 GitHub 仓库只提供 Skill 与客户端代码。飞书 App Secret 只保存在托管 Contribution Gateway 服务端，普通贡献者永远不需要获得它。

## Current V1 identity model

默认模式：

```text
FORTIOR_GATEWAY_MODE=open
```

当前没有强身份认证：

- `contributor.username` 是用户声明的稳定用户名；
- `client_instance_id` 是安装器生成的随机 UUID；
- 来源 IP、用户名和 client instance 只能作为弱风控信号；
- 任何字段都不能被当作实名或已验证身份。

## Current server-side controls

以下能力已经在 Gateway 服务端实现，而不是只存在于客户端：

### Request size

Gateway 对总 payload 大小设置上限，当前默认 128 KiB。

### Mandatory payload checks

Gateway 会检查：

- contribution type；
- `contributor.username`；
- 可见范围 / 署名 / 披露权限等 mandatory submission preferences；
- `rights_confirmed=true`。

### Short-term exact dedupe

Gateway 对规范化 payload 计算 SHA-256 `content_hash`，在当前进程内对短期完全重复内容抑制重复写入。

### Lightweight rate limit

当前按弱信号组合限流：

- 来源 IP；
- `contributor.username`；
- `client_instance_id`。

这些信号都可以被共享、变化或主动重置，因此只适合防误操作和低强度滥用，不是身份安全边界。

### Feishu write serialization and retry

当前单进程 Gateway 对 Experience / Review Point 两张目标表分别使用写锁，避免同一进程内对同一表并发写；对飞书瞬时网络异常以及 `1254290` / `1254291` 做有限次数的退避重试。

### Governance isolation

提交成功后只进入飞书待治理数据，不会直接成为 FortiorReviewPoints 正式知识。

## Current client-side protections

Skill/runtime 还会进行本地隐私和格式预检，例如：

- Schema / required field 检查；
- payload 大小检查；
- 高置信私钥 / Token 模式检查；
- 用户明确选择公开范围和源信息披露边界。

**这些客户端检查不能被当作不可绕过的服务端安全能力。** 开源客户端可以被修改，恶意用户也可以自己构造 HTTP 请求。

## Not implemented as strong server guarantees yet

以下内容目前属于后续增强，不应在文档里描述成已经完全实现：

- 强实名 / GitHub / 飞书 / SSO 身份验证；
- 持久化跨实例限流；
- 持久化跨重启幂等和去重；
- 服务端完整 Secret/DLP 扫描；
- 每字段长度和数组元素的完整服务端限制；
- 共享持久化写队列；
- 用户信誉、封禁名单和审计后台。

## Optional edit-code mode

如果开放入口出现明显垃圾提交，可以在不引入账号系统的情况下把 Gateway 改成：

```text
FORTIOR_GATEWAY_MODE=edit_code
```

并在服务端配置：

```text
FORTIOR_GATEWAY_EDIT_CODE=<secret>
```

客户端提交时使用：

```text
X-Fortior-Edit-Code: ...
```

编辑码可以按团队或个人分配并随时轮换。它仍然不是账号身份，但可以显著降低完全公开入口的滥用概率。

## Future optional identity

未来可以增加 GitHub、飞书或企业 SSO 等验证，用于：

- 提高额度；
- 提升贡献信誉；
- 提供可信署名；
- 加速治理；
- 精细化封禁和审计。

除非治理策略明确改变，否则不应把第三方账号作为公共贡献的唯一入口。

## Feishu governance metadata

Engineering Experience 表会保存较完整的贡献元数据，包括提交 ID、贡献用户名、公开权限、client instance、内容哈希、客户端版本和治理状态。

现有 Review Point 表使用兼容映射：已有业务字段保持不删不改，额外治理/来源信息根据现有表结构写入对应字段或备注，而不是强制迁移成另一套表结构。

## Important boundary

```text
客户端 Skill
→ 帮助正常用户正确、安全地贡献

Gateway
→ 当前不可绕过的服务端入口控制

Feishu
→ 待治理数据存储

Owner / expert governance
→ 决定是否采纳、补充、拒绝、合并或发布
```

飞书 Secret 永远不进入普通贡献者客户端，也不要在 Issue、聊天、截图或测试日志中公开。
