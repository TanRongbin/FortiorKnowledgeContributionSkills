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

### Structured interaction rule — mandatory when supported

If the host Agent/CLI provides a structured question capability such as `AskUserQuestion`, `UserQuestion`, a choice picker, single-select, multi-select, or equivalent interactive prompt, **MUST use that capability for the mandatory questionnaire**.

Do not first print the questionnaire as ordinary prose and wait for the user to type answers when a structured interaction tool is available.

Use the structured interaction as follows:

- free-text input for `contributor.username` or a custom title/display name when required;
- single-select for attribution, visibility, contribution type when unclear, and title keep/edit confirmation;
- multi-select or an equivalent compact choice interaction for source-disclosure permissions;
- a single explicit confirmation choice for rights/privacy confirmation;
- group multiple compatible questions into one structured interaction when the host supports it, to minimize user turns.

If the host does **not** expose any structured question capability, fall back to one compact text prompt with numbered/clearly labeled choices. This fallback is allowed only because the host lacks the interactive capability, not because prose is easier.

If a structured interaction call fails, retry it once when reasonable; only then fall back to text and state that the CLI interaction capability was unavailable.

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

### Submission transport is the bundled runtime, not an Agent tool

Do **not** search the current Agent tool list for a dedicated `Fortior Contribution Gateway` tool and do **not** conclude that submission is unavailable merely because no such tool is listed.

The installer provides a stable local runtime at:

```text
~/.fortior/runtime/fortior-knowledge-contributor/scripts/submit.py
```

Submission procedure:

1. Serialize each approved contribution to a temporary UTF-8 JSON file. The submit runtime also accepts UTF-8 BOM files.
2. Execute the bundled runtime with the local shell/process tool that is already available to the Agent:

```text
python ~/.fortior/runtime/fortior-knowledge-contributor/scripts/submit.py --type experience --file <payload.json>
python ~/.fortior/runtime/fortior-knowledge-contributor/scripts/submit.py --type review_point --file <payload.json>
```

On Windows, expand `~`/`$HOME` to the user's home directory as needed. If `python` is unavailable, use the platform's configured Python launcher.

3. The runtime itself loads `~/.fortior/knowledge-contributor.env` and decides whether to use `gateway`, `feishu_direct`, or `local_only`. Do not ask the user to restate a Gateway endpoint that is already present in that config.
4. If the stable runtime path is missing, fall back to the loaded Skill's own `scripts/submit.py`. Known personal Skill locations include `~/.agents/skills/fortior-knowledge-contributor`, `~/.claude/skills/fortior-knowledge-contributor`, and `~/.gemini/skills/fortior-knowledge-contributor`.
5. Report the submit runtime's real result. Only say submission succeeded when it returns `Submission: PASS`. Preserve and surface the exact configuration/network/server error when it fails.
6. Remove temporary payload files after submission unless they are intentionally retained as a local draft.

If the user approved both an Engineering Experience and a Review Point, submit them as **two separate payloads** after the shared questionnaire/preview; do not stop after preparing both drafts.

Production path:

```text
Skill → bundled submit.py → open Fortior Contribution Gateway → Feishu
```

No account login is required by the Skill.

The Gateway may later enable a non-account `edit_code` mode. If the server reports that an edit code is required, ask the user for the code or tell them where to configure it; do not redirect them to GitHub login.

Successful submission means **entered governance**, not **approved into FortiorReviewPoints**.
