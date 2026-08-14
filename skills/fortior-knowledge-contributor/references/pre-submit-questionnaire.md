# Mandatory Pre-Submission Questionnaire

Ask only unanswered items. Prefer one compact grouped question.

## A. Contributor username — required

Ask:

> 本次贡献记录使用什么用户名？可以是真名、昵称、公司内部昵称或其他稳定名称，不要求 GitHub/飞书账号。

Store as `contributor.username`.

Never require the user to create a third-party account.

## B. Contribution type — required if unclear

Choose:

- 工程经验 `engineering_experience`
- 程序评审点 `review_point`

## C. Visibility — explicit user choice

Choose one:

1. `public` — 可以在未来公开知识库/Sites 发布。
2. `anonymized_public` — 技术内容可公开，但公开时隐藏或替换个人/项目身份信息。
3. `private_governance_only` — 只供治理人员查看，不允许公开发布。

Never infer this choice from repository visibility.

## D. Attribution

Choose one:

- `username`
- `display_name`
- `anonymous`

## E. Source disclosure

Explicitly allow/deny:

- repository name
- commit id
- relative file paths
- minimal code excerpts

## F. Rights / privacy confirmation

Require explicit confirmation that:

- the contributor has the right to submit the material;
- no secret/password/token/private key or unnecessary customer/personal information is included;
- the selected visibility level is understood.

If they cannot confirm, save locally only.

## G. Title confirmation

Show the AI-proposed title and ask to keep or edit it.

## Optional, never required

You may ask for a GitHub username, company, team or contact only if the user wants to provide it. Absence of those values must never block contribution.
