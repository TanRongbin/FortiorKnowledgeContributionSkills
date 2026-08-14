---
name: fortior-knowledge-contributor
description: Capture a solved software or embedded engineering issue as structured Engineering Experience, or abstract evidence into a reusable Review Point; ask mandatory contributor/publication questions before submission. No third-party account login is required.
---

# Fortior Knowledge Contributor

## Core rule

This skill must remain usable by **any installed user**. Do not require GitHub, Feishu, company SSO or another third-party account before contribution.

A user-chosen `contributor.username` is required for provenance, but it is a declared username, not verified identity.

## Two outputs

1. `engineering_experience`: what happened in one real engineering case.
2. `review_point`: a reusable review/control rule for future projects.

Do not treat them as equivalent.

## Trigger examples

- 把刚刚解决的问题贡献一下
- 总结成工程经验并提交
- 把这个问题沉淀下来
- 总结成评审点并贡献
- contribute this solved issue

If the user does not specify a type, prefer `engineering_experience`.

## Phase 1 — Recover the real issue

Use the current session first. Do not force the user to restate information already available.

When relevant, inspect:

```bash
git status --short
git diff
git diff --staged
git log -5 --oneline
git branch --show-current
git rev-parse HEAD
git remote -v
```

Use relevant tests, logs, waveforms, traces and user confirmation.

## Phase 2 — Separate evidence from inference

Root cause confidence:

- `confirmed`
- `strong_hypothesis`
- `unconfirmed`

Never promote a guess just to fill a field.

## Phase 3 — Draft

Experience preserves:

`problem → symptom → trigger → investigation → root cause → solution → verification → benefit → lesson → scope → evidence`

Review Point preserves:

`review question → inspection → failure criteria → trigger → risk → correct practice → verification → scope → evidence`

## Phase 4 — Mandatory user questionnaire

Read `references/pre-submit-questionnaire.md` and ask only unanswered mandatory items.

Rules:

- `contributor.username` is mandatory.
- Do **not** require a GitHub username.
- Do **not** require Feishu login.
- Publication/privacy choices must be explicitly selected by the user.
- If already answered in the conversation, do not ask again.
- Show the proposed title and allow keep/edit.

## Phase 5 — Privacy check

Read `references/evidence-and-privacy.md`.

Do not submit secrets, credentials, unnecessary customer/personal data or irrelevant proprietary code.

## Phase 6 — Preview

Show:

- type
- title
- contributor username
- publication level / attribution
- root cause or review question
- solution or failure criteria
- verification / evidence
- source disclosure choices
- uncertainty

## Phase 7 — Submit

If the user explicitly asked to contribute/submit/upload and the mandatory questionnaire is complete, remote submission is allowed after preview.

If the user only asked to summarize, stop at local draft.

Production path:

```text
Skill → open Fortior Contribution Gateway → Feishu
```

No account login is required by the Skill.

The Gateway may later enable a non-account `edit_code` mode. If the server reports that an edit code is required, ask the user for the code or tell them where to configure it; do not redirect them to GitHub login.

Successful submission means **entered governance**, not **approved into FortiorReviewPoints**.
