# Mandatory Pre-Submission Questionnaire

Ask only unanswered items.

## Interaction policy

When the host Agent/CLI exposes a structured question facility such as `AskUserQuestion`, a choice picker, single-select, multi-select, or equivalent interactive form, **use it instead of ordinary prose for this questionnaire**.

Do not print all choices as plain text and wait for the contributor to manually type answers when the host can present selectable options.

Recommended control types:

- `contributor.username`: free-text input, or a choice with `Other`/custom input if that is the host's supported pattern;
- attribution: single-select;
- contribution type when unclear: single-select;
- visibility: single-select;
- source disclosure: multi-select, or a compact equivalent that lets the user explicitly allow/deny repository, commit, paths and minimal code excerpts;
- title keep/edit: single-select with custom/edit path;
- rights/privacy: explicit confirmation choice.

Prefer **one compact grouped structured interaction** so the contributor normally answers everything in one round. If the host cannot combine different control types in one interaction, use the smallest practical number of structured prompts.

Only if no structured-question capability exists may the Agent fall back to one compact text prompt with clearly labeled choices.

## A. Contributor username + attribution — required

Collect both together when the host supports grouped questions:

- stable username: real name, nickname, company-internal nickname, or another stable chosen name; no GitHub/Feishu account is required;
- attribution: `username` / `display_name` / `anonymous`.

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

## Recommended compact first-round interaction

When the type is already clear, collect these in one structured interaction when supported:

1. username + attribution;
2. visibility;
3. source disclosure (repository / commit / paths / code excerpt);
4. title keep/edit + rights/privacy confirmation.

Only ask a follow-up when an answer is genuinely ambiguous or incomplete.

## Optional, never required

You may ask for a GitHub username, company, team or contact only if the user wants to provide it. Absence of those values must never block contribution.
