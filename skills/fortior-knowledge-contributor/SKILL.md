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

### Review Point field-completion pass

Before previewing a `review_point`, perform one explicit completion pass over the current conversation, repository evidence and already-read engineering material. Populate the following optional fields whenever the information is actually supported:

- `problem_category`: one compact, reusable technical category; avoid sentence-length labels.
- `engineering_series`: applicable Fortior/product series.
- `project_product`: project/product identifier only when known and disclosure is appropriate.
- `chip_models`: concrete MCU/SoC/chip model names.
- `cpu_architectures`: e.g. 8051, RISC-V; use exact evidence rather than guessing from filenames.
- `program_modules`: affected logical modules such as UART/Communication, FOC, speed loop, protection, bootloader.
- `runtime_stages`: compile/link, startup, ISR/runtime, steady-state, protection/fault handling, etc., only when supported.
- `code_symbols`: relevant variables/functions/macros/structures actually seen in evidence.
- `root_cause_confidence`: use the confidence rules above.
- `evidence_types`: describe the actual evidence classes used, e.g. source review, Git diff/commit, log, waveform, trace, test, engineering document, user confirmation.
- `non_applicable_conditions`: explicit exclusions or cases where this review point should not be applied.
- `sensitive_information_status`: `no_sensitive_info`, `sanitized`, or `restricted` based on the final payload/privacy boundary.

This completion pass is **additive**. Do not remove or shorten the existing Review Point content just to fit these fields. If a field cannot be established from evidence, leave it empty instead of asking unnecessary questions or inventing a value.

When source disclosure is disabled, do not reconstruct a repository/product/file identity merely to fill these fields. Technical metadata already explicitly provided by the user may still be used if it is within the approved publication boundary.

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

For Review Points, also mention any populated engineering context that materially narrows applicability (series/chip/CPU/module/stage) so the user can catch an incorrect classification before submission.

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
