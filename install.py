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


def install_to(base: Path) -> Path:
    dst = base.expanduser().resolve() / SKILL_NAME
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(SOURCE, dst)
    return dst


def ensure_local_config() -> Path:
    config_dir = HOME / ".fortior"
    config_dir.mkdir(parents=True, exist_ok=True)
    config = config_dir / "knowledge-contributor.env"
    example = SOURCE / "config.example.env"
    if not config.exists():
        shutil.copy2(example, config)

    text = config.read_text(encoding="utf-8")
    marker = "FORTIOR_CLIENT_INSTANCE_ID="
    lines = text.splitlines()
    changed = False
    for i, line in enumerate(lines):
        if line.startswith(marker) and not line[len(marker):].strip():
            lines[i] = marker + str(uuid.uuid4())
            changed = True
            break
    if not any(line.startswith(marker) for line in lines):
        lines.append(marker + str(uuid.uuid4()))
        changed = True
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
    config = ensure_local_config()

    print("Installed Fortior skill:")
    for path in installed:
        print(f"  - {path}")
    print(f"Local config: {config}")
    print("No GitHub/Feishu account is required to use the skill.")


if __name__ == "__main__":
    main()
