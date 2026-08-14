# Mandatory Pre-Submission Questionnaire

Ask only unanswered items, but every mandatory field below must have an explicit value before remote submission.

Prefer one compact grouped question rather than a long interview.

## Required

### A. Contributor username

Ask:

> 本次贡献记录的用户名是什么？可以使用 GitHub 用户名、公司内部昵称或你希望在治理记录中使用的稳定用户名。

Store as `contributor.username`.

If GitHub CLI or Git config suggests a name, you may offer it as a default, but the user must confirm it.

### B. Contribution type

If not already explicit, ask the user to choose:

- 工程经验 `engineering_experience`
- 程序评审点 `review_point`

### C. Visibility

The user must choose one:

1. `public` — 内容可在未来公开知识库/Sites 中发布。
2. `anonymized_public` — 内容可公开，但公开时隐藏/替换个人或项目身份信息。
3. `private_governance_only` — 只允许治理人员查看，不允许公开发布。

Never infer this from repository visibility.

### D. Attribution when published

Choose one:

- `username`
- `display_name`
- `anonymous`

Even when public attribution is anonymous, internal governance may retain `contributor.username` for abuse handling and provenance.

### E. Source disclosure

Ask the user to explicitly allow or deny each:

- repository name
- commit id
- relative file paths
- minimal code excerpts

Store four booleans. A denied item must be removed or anonymized from any public output.

### F. Rights / privacy confirmation

Require an explicit confirmation that:

- the contributor has the right to submit the material;
- secrets, passwords, tokens, private keys and unnecessary personal/customer information are not included;
- they understand the selected visibility level.

If the user cannot confirm, save locally only and do not submit remotely.

### G. Title confirmation

Show the AI-proposed title and ask whether to:

- keep it; or
- replace it with user-provided text.

## Recommended when relevant

Ask for applicability/scope when AI cannot reliably infer it, for example:

- MCU / CPU family
- software module
- motor/application type
- protocol
- frontend/backend/embedded/algorithm/toolchain

Do not fabricate missing scope metadata.
