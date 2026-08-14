# Architecture

## Knowledge layers

```text
Engineering Evidence
(code / diff / commit / log / waveform / test)
          ↓
Engineering Experience
(problem / investigation / root cause / fix / verification)
          ↓
Review Knowledge
(review question / inspection / failure criteria / correct practice)
```

Experience 与 Review Point 是不同知识实体。

允许：

```text
EXP-000142 ─┐
EXP-000193 ─┼──→ RP-000087
EXP-000251 ─┘
```

但一条 Experience 不需要、也不应该自动升级成 Review Point。

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
local validation + privacy scan
  ↓
Gateway (production) / Feishu direct (owner only)
  ↓
Feishu pending governance table
  ↓
Owner governance
  ↓
FortiorReviewPoints experiences/ or review-points/
```

## Trust boundary

客户端 Skill 是开源代码，不能承担强制安全边界。任何人都可以 fork、删除本地检查或自行构造 HTTP 请求。

因此：

- 客户端检查用于帮助正常用户避免误提交；
- Gateway 才负责真实身份、速率限制、重复检测、垃圾检测、封禁和审计；
- 飞书 App Secret 永远不发给普通贡献者；
- 飞书中的记录默认是 `待治理`，提交成功不代表知识已获批准。
