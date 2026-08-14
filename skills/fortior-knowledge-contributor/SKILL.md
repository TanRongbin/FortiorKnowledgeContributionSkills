---
name: fortior-knowledge-contributor
description: Capture a solved software or embedded engineering issue as structured Engineering Experience, or abstract evidence into a reusable Review Point; ask the contributor mandatory publication/privacy questions before any submission.
---

# Fortior Knowledge Contributor

## Scope

This skill has two outputs:

1. `engineering_experience`: what actually happened in one real engineering case.
2. `review_point`: a reusable review/control rule for future projects.

Do not treat them as equivalent.

## Typical triggers

- 把刚刚解决的问题贡献一下
- 总结成工程经验
- 把这个问题沉淀下来
- 总结成评审点
- 把这次修改抽象成审查项
- contribute this solved issue

If the user does not specify a type, default to `engineering_experience` unless the intent is clearly a reusable review rule.

## Phase 1 — Recover the real issue

Use information already available in the current session first. Do not force the user to restate it.

When relevant and permitted, inspect:

```bash
git status --short
git diff
git diff --staged
git log -5 --oneline
git branch --show-current
git rev-parse HEAD
git remote -v
```

Read only relevant files. Use available tests, logs, traces, waveforms, screenshots and user confirmation.

## Phase 2 — Separate evidence from inference

Root cause confidence must be one of:

- `confirmed`
- `strong_hypothesis`
- `unconfirmed`

Never promote a guess merely to complete a field.

## Phase 3 — Draft the contribution

For Experience, preserve:

`problem → symptom → trigger → investigation → root cause → solution → verification → benefit → lesson → scope → evidence`

For Review Point, preserve:

`review question → inspection → failure criteria → trigger → risk → correct practice → verification → scope → evidence`

Review Point titles should be control/review concepts, not bug-story titles.

## Phase 4 — Mandatory contributor questionnaire

Before creating the final submission payload, read `references/pre-submit-questionnaire.md` and ask all mandatory unanswered items.

Important:

- `contributor.username` is required.
- Publication/privacy choices must come from the user, not AI inference.
- If the user has already answered one item clearly in the current conversation, do not ask it again.
- Show the AI-proposed title and allow the user to keep or edit it.

## Phase 5 — Privacy and evidence check

Read `references/evidence-and-privacy.md`.

Do not submit secrets, credentials, customer personal data or irrelevant proprietary code.

If private code exists, sanitize before upload and accurately set privacy/disclosure fields.

## Phase 6 — Preview

Show a concise final preview with:

- type
- title
- contributor username
- publication level and attribution
- root cause / review question
- solution / failure criteria
- verification / evidence
- source disclosure choices
- uncertainty

Do not silently send a materially different payload.

## Phase 7 — Submit

A user's explicit request to “贡献/提交/上传” plus completion of the mandatory questionnaire authorizes submission of the previewed payload. If they only asked to “总结”, stop after generating the local draft unless they then ask to submit.

Save JSON under `.contributions/` when practical.

Validate locally with the bundled submission script in dry-run mode before real submission.

Production path:

```text
Skill → authenticated Fortior Contribution Gateway → Feishu
```

Owner-only internal path:

```text
Skill → Feishu direct mode
```

Never expose an Owner Feishu secret to a normal contributor.

## Completion report

Report:

- contribution type
- title
- contributor username
- local JSON path (if written)
- validation result
- submission result
- remote submission/record ID if returned
- governance note

A successful submission means **entered governance**, not **approved into FortiorReviewPoints**.
