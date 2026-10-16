"""Read-only validation for optional synthesis metadata. No network or approval."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def refs(value: object, known: set[str]) -> list[str]:
    need(isinstance(value, list) and all(nonempty(x) for x in value), "evidence_ids must be strings")
    need(len(set(value)) == len(value) and set(value) <= known, "duplicate or unknown evidence reference")
    return value


def _validate_extension(payload: dict) -> None:
    need(isinstance(payload, dict), "payload must be an object")
    extension = payload.get("knowledge_extension")
    if extension is None:
        return  # Old payloads remain valid; base-schema validation is separate.
    need(isinstance(extension, dict), "knowledge_extension must be an object")
    need(extension.get("schema_version") == "fortior.capture-enrichment.v1", "unsupported enrichment schema")
    need(extension.get("relation_intent") in {"new_case", "supporting_evidence", "refine", "counterexample", "correction", "unknown"}, "invalid relation_intent")
    need(extension.get("independence") in {"independent_case", "same_case_followup", "copied_reference", "unknown"}, "invalid independence")
    need(nonempty(extension.get("mechanism")) and nonempty(extension.get("contribution_delta")), "mechanism and contribution_delta required; unknown is permitted")
    ids = extension.get("related_ids", [])
    need(isinstance(ids, list) and all(nonempty(x) for x in ids), "related_ids must be strings")
    facts = extension.get("evidence_facts")
    need(isinstance(facts, list) and all(isinstance(f, dict) for f in facts), "evidence_facts must be objects")
    known: set[str] = set()
    for fact in facts:
        key = fact.get("id")
        need(nonempty(key) and key not in known, "empty or duplicate evidence id")
        known.add(key)
        need(nonempty(fact.get("statement")), "evidence statement missing")
        need(fact.get("confidence") in {"confirmed", "strong_hypothesis", "unconfirmed"}, "invalid evidence confidence")
        source = fact.get("source_ref")
        need(isinstance(source, dict) and nonempty(source.get("locator")), "structured source_ref with locator required")
    boundaries = extension.get("boundary_conditions", [])
    need(isinstance(boundaries, list), "boundary_conditions must be an array")
    for boundary in boundaries:
        need(isinstance(boundary, dict) and nonempty(boundary.get("condition")), "invalid boundary condition")
        refs(boundary.get("evidence_ids"), known)
    counters = extension.get("counterexamples", [])
    need(isinstance(counters, list), "counterexamples must be an array")
    for counter in counters:
        need(isinstance(counter, dict) and nonempty(counter.get("question")), "invalid counterexample")
        need(counter.get("result") in {"excluded", "present", "unknown"}, "invalid counterexample status")
        evidence = refs(counter.get("evidence_ids"), known)
        need(counter["result"] == "unknown" or bool(evidence), "observed/excluded counterexample needs evidence")
    verification = extension.get("verification")
    need(isinstance(verification, dict), "verification object required")
    need(verification.get("status") in {"passed", "failed", "not_run", "unknown"}, "invalid verification status")
    need(isinstance(verification.get("expected_behavior"), str) and isinstance(verification.get("observed_behavior"), str), "verification text missing")
    evidence = refs(verification.get("evidence_ids"), known)
    need(verification["status"] not in {"passed", "failed"} or bool(evidence), "executed verification needs evidence")


def validate_extension(payload: dict) -> None:
    need(isinstance(payload, dict), "payload must be an object")
    # Legacy payloads are validated by their existing base schema.
    pending = [(payload.get("knowledge_extension"), 0)]
    nodes = characters = 0
    while pending:
        value, depth = pending.pop()
        nodes += 1
        need(depth <= 64 and nodes <= 250_000, "extension exceeds nesting/node limit")
        if isinstance(value, str):
            characters += len(value)
            need(len(value) <= 1_000_000 and characters <= 32_000_000, "extension exceeds text limit")
        elif isinstance(value, dict):
            need(all(isinstance(k, str) for k in value), "extension keys must be strings")
            pending.extend((v, depth + 1) for pair in value.items() for v in pair)
        elif isinstance(value, list):
            pending.extend((v, depth + 1) for v in value)
        else:
            need(value is None or type(value) in (bool, int, float), "extension contains non-JSON value")
            if isinstance(value, float):
                need(value == value and abs(value) != float("inf"), "extension contains non-finite number")
    try:
        _validate_extension(payload)
    except (TypeError, KeyError, AttributeError) as exc:
        raise ValueError("extension field has invalid type or missing key") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8-sig"))
        validate_extension(payload)
        print(json.dumps({"ok": True, "structural_only": True, "extension_present": payload.get("knowledge_extension") is not None}))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
