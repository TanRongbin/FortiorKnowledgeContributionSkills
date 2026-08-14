# Mandatory Pre-Submission Questionnaire

Ask only unanswered items. Prefer **one compact grouped question** so the contributor normally answers everything in one round.

## A. Contributor username + attribution — required

Ask both together:

> 本次贡献记录使用什么稳定用户名？公开时采用哪种署名方式？用户名可以是真名、昵称、公司内部昵称或其他稳定名称，不要求 GitHub/飞书账号。
>
> 署名方式请选择：`username`（用户名） / `display_name`（显示名） / `anonymous`（匿名）。

Store the stable name as `contributor.username` and the publication choice as `submission_preferences.attribution`.

If the user says things like “Terry署名”“用用户名署名”“匿名”，map them directly and **do not ask a second attribution question**.

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

## D. Source disclosure — explicit user choice

Explicitly allow/deny each of:

- repository name
- commit id
- relative file paths
- minimal code excerpts

If the user says “无”“均不披露”“全部不公开”，map all four to `false` and **do not ask four separate follow-ups**.

## E. Rights / privacy confirmation

Require explicit confirmation that:

- the contributor has the right to submit the material;
- no secret/password/token/private key or unnecessary customer/personal information is included;
- the selected visibility level is understood.

If they cannot confirm, save locally only.

## F. Title confirmation

Show the AI-proposed title and ask to keep or edit it.

## Recommended compact first-round prompt

When the type is already clear, group the remaining items into one interaction:

1. username + attribution;
2. visibility;
3. source disclosure (repository / commit / paths / code excerpt);
4. title keep/edit + rights/privacy confirmation.

Only ask a follow-up when an answer is genuinely ambiguous or incomplete.

## Optional, never required

You may ask for a GitHub username, company, team or contact only if the user wants to provide it. Absence of those values must never block contribution.
