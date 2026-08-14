#!/usr/bin/env python3
"""Cross-platform installer for Fortior Agent Skills."""
from __future__ import annotations

import argparse
import shutil
import uuid
from pathlib import Path

SKILL_NAME = "fortior-knowledge-contributor"
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "skills" / SKILL_NAME
HOME = Path.home()
RUNTIME = HOME / ".fortior" / "runtime" / SKILL_NAME

TARGETS = {
    "agents": HOME / ".agents" / "skills",
    "codex": HOME / ".agents" / "skills",
    "copilot": HOME / ".agents" / "skills",
    "claude": HOME / ".claude" / "skills",
    "gemini": HOME / ".gemini" / "skills",
}

DETECT = {
    "agents": ("codex",),
    "claude": ("claude",),
    "gemini": ("gemini",),
    "copilot": ("copilot", "gh"),
}


def detected_targets() -> list[str]:
    found: list[str] = []
    for target, commands in DETECT.items():
        if any(shutil.which(cmd) for cmd in commands):
            found.append(target)
    if "agents" in found and "copilot" in found:
        found.remove("copilot")
    return found or ["agents"]


def copy_skill(dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(SOURCE, dst)
    return dst


def install_to(base: Path) -> Path:
    return copy_skill(base.expanduser().resolve() / SKILL_NAME)


def install_runtime() -> Path:
    """Install an agent-independent executable copy used by SKILL.md at submit time."""
    return copy_skill(RUNTIME)


def config_value(path: Path, key: str) -> str:
    marker = key + "="
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith(marker):
            return line[len(marker):].strip()
    return ""


def set_config_line(lines: list[str], key: str, value: str) -> bool:
    marker = key + "="
    for i, line in enumerate(lines):
        if line.startswith(marker):
            if line[len(marker):].strip() != value:
                lines[i] = marker + value
                return True
            return False
    lines.append(marker + value)
    return True


def ensure_local_config() -> Path:
    config_dir = HOME / ".fortior"
    config_dir.mkdir(parents=True, exist_ok=True)
    config = config_dir / "knowledge-contributor.env"
    example = SOURCE / "config.example.env"
    if not config.exists():
        shutil.copy2(example, config)

    text = config.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    changed = False

    instance_marker = "FORTIOR_CLIENT_INSTANCE_ID="
    for i, line in enumerate(lines):
        if line.startswith(instance_marker) and not line[len(instance_marker):].strip():
            lines[i] = instance_marker + str(uuid.uuid4())
            changed = True
            break
    if not any(line.startswith(instance_marker) for line in lines):
        lines.append(instance_marker + str(uuid.uuid4()))
        changed = True

    desired_version = config_value(example, "FORTIOR_CLIENT_VERSION")
    if desired_version:
        changed = set_config_line(lines, "FORTIOR_CLIENT_VERSION", desired_version) or changed

    desired_mode = config_value(example, "FORTIOR_SUBMIT_MODE")
    desired_endpoint = config_value(example, "FORTIOR_CONTRIBUTION_ENDPOINT")
    current_mode = ""
    current_endpoint = ""
    for line in lines:
        if line.startswith("FORTIOR_SUBMIT_MODE="):
            current_mode = line.split("=", 1)[1].strip()
        elif line.startswith("FORTIOR_CONTRIBUTION_ENDPOINT="):
            current_endpoint = line.split("=", 1)[1].strip()

    # Safely migrate old/default installs to the hosted Gateway. Preserve explicit
    # owner direct-write mode and custom non-local Gateway endpoints.
    if desired_mode and current_mode in {"", "local_only"}:
        changed = set_config_line(lines, "FORTIOR_SUBMIT_MODE", desired_mode) or changed
        current_mode = desired_mode

    endpoint_is_legacy = (
        not current_endpoint
        or current_endpoint.startswith("http://127.0.0.1")
        or current_endpoint.startswith("http://localhost")
        or current_endpoint.startswith("https://127.0.0.1")
        or current_endpoint.startswith("https://localhost")
    )
    if desired_endpoint and current_mode != "feishu_direct" and endpoint_is_legacy:
        changed = set_config_line(lines, "FORTIOR_CONTRIBUTION_ENDPOINT", desired_endpoint) or changed

    if changed:
        config.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Fortior knowledge contribution skill")
    parser.add_argument("--target", choices=["auto", "all", "agents", "codex", "copilot", "claude", "gemini", "custom"], default="auto")
    parser.add_argument("--path", help="Custom skills directory for --target custom")
    args = parser.parse_args()

    if not SOURCE.joinpath("SKILL.md").exists():
        raise SystemExit(f"Missing skill source: {SOURCE}")

    if args.target == "custom":
        if not args.path:
            raise SystemExit("--target custom requires --path")
        bases = [Path(args.path)]
    elif args.target == "auto":
        bases = [TARGETS[t] for t in detected_targets()]
    elif args.target == "all":
        bases = list(dict.fromkeys(TARGETS.values()))
    else:
        bases = [TARGETS[args.target]]

    installed = [install_to(base) for base in dict.fromkeys(bases)]
    runtime = install_runtime()
    config = ensure_local_config()

    print("Installed Fortior skill:")
    for path in installed:
        print(f"  - {path}")
    print(f"Stable runtime: {runtime}")
    print(f"Submit runtime: {runtime / 'scripts' / 'submit.py'}")
    print(f"Local config: {config}")
    print("Hosted Gateway: https://fortior-knowledge-contribution-gateway.onrender.com")
    print("No GitHub/Feishu account is required to use the skill.")


if __name__ == "__main__":
    main()
