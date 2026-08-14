# Architecture

## Knowledge layers

```text
Engineering Evidence
(code / diff / commit / log / waveform / test / user confirmation)
          ↓
Engineering Experience
(problem / investigation / root cause / fix / verification)
          ↓
Review Point
(review question / inspection / failure criteria / correct practice)
```

Engineering Experience 与 Review Point 是不同知识实体。

允许多个经验共同支持一个评审点：

```text
EXP-000142 ─┐
EXP-000193 ─┼──→ RP-000087
EXP-000251 ─┘
```

但一条 Experience 不需要、也不应该自动升级成通用 Review Point。

## Contribution flow

```text
AI coding session
  ↓
fortior-knowledge-contributor
  ↓
automatic evidence extraction
  ↓
structured draft
  ↓
mandatory user questionnaire
  ↓
local validation + privacy pre-check
  ↓
bundled submit runtime
  ↓
public Fortior Contribution Gateway
  ↓
Feishu pending-governance data
  ├─ Engineering Experience table
  └─ existing Review Point table
  ↓
Owner / expert governance
  ↓
downstream governed knowledge / FortiorReviewPoints publication flow
```

`feishu_direct` 只用于 Owner/维护者调试，不是普通贡献者路径。

## Hosted Gateway

普通贡献者默认使用：

```text
https://fortior-knowledge-contribution-gateway.onrender.com
```

Gateway 提供：

```text
GET  /health
GET  /ready
POST /v1/contributions
```

`/health` 只证明服务进程可运行；`/ready` 还会验证飞书认证以及 Experience / Review Point 两张目标表是否可访问。

## Identity model

当前 V1 **没有真实身份认证**。

- `contributor.username` 是贡献者声明的稳定用户名；
- `client_instance_id` 是安装时生成的弱客户端信号；
- 两者都不能证明真实身份；
- GitHub / 飞书 / 企业 SSO 目前都不是贡献前置条件。

因此不要把 `username`、`client_instance_id` 或来源 IP 表述成可信实名身份。

## Trust boundary

客户端 Skill 是开源代码，任何人都可以 fork、修改或绕过本地检查。因此：

- 客户端检查主要帮助正常用户避免误提交；
- Gateway 承担服务端必填校验、请求大小限制、短期去重、轻量限流、飞书写入串行化与重试；
- 飞书 App Secret 永远不发给普通贡献者；
- 飞书中的记录默认是待治理数据；
- `Submission: PASS` 只表示进入治理入口，不表示知识已经获批。

## Current persistence boundary

当前 Gateway 的限流桶和短期去重状态保存在单进程内存中。Render Free 单实例阶段足以进行当前小规模测试；如果未来需要多实例或更高并发，应把：

```text
rate limit
idempotency / dedupe
write queue
```

迁移到共享持久化存储。

## Governance boundary

本仓库负责 **知识采集与提交入口**，不在这里定义 FortiorReviewPoints 的最终批准、版本发布和正式 Review Pack 规则。

Experience / Review Point 进入飞书后仍需要 Owner/专家治理；后续如何映射到 FortiorReviewPoints、Sites 或其他发布层，应由对应治理契约决定，而不是由 Contribution Skill 自动推断。
