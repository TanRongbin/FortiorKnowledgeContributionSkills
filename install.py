#!/usr/bin/env python3
"""Cross-platform installer for Fortior Agent Skills."""
from __future__ import annotations

import argparse
import shutil
import uuid
import json
import sys
import tempfile
from pathlib import Path

SKILL_NAME = "fortior-knowledge-contributor"
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "skills" / SKILL_NAME
sys.dont_write_bytecode = True
sys.path.insert(0, str(SOURCE / 'scripts'))
from local_identity import install_tree, seal, source_identity, verify
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


def copy_skill(dst: Path, *, replace: bool = False) -> Path:
    """Build from local source, verify, then replace with a recoverable backup."""
    identity = source_identity(ROOT)
    if identity['dirty']:
        raise ValueError('Source repository is dirty; preserve/commit your work before distributing it')
    with tempfile.TemporaryDirectory(prefix='fortior-contribution-install-') as temporary:
        stage = Path(temporary) / SKILL_NAME
        shutil.copytree(SOURCE, stage, symlinks=True,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
        seal(stage, skill=SKILL_NAME, source=identity)
        installed = install_tree(stage, dst, replace=replace, protected_root=ROOT)
        print(json.dumps({k:v for k,v in installed.items() if k != 'identity'}, ensure_ascii=False))
    return dst


def install_to(base: Path, *, replace: bool = False) -> Path:
    return copy_skill(base.expanduser().absolute() / SKILL_NAME, replace=replace)


def install_runtime(*, replace: bool = False) -> Path:
    """The user-facing Skill and submission runtime must have identical source bytes."""
    return copy_skill(RUNTIME, replace=replace)



def install_destinations(destinations: list[Path], *, replace: bool) -> list[Path]:
    """One manual update: all selected Skill/runtime copies or recover old copies."""
    identity=source_identity(ROOT)
    if identity['dirty']:raise ValueError('Source repository is dirty; preserve/commit your work first')
    destinations=list(dict.fromkeys(p.expanduser().absolute() for p in destinations))
    config=HOME/'.fortior'/'knowledge-contributor.env'
    if any(p.is_symlink() for p in (config,*config.parents)):raise ValueError('configuration symlink rejected')
    previous_config=config.read_bytes() if config.exists() else None
    changes=[]
    with tempfile.TemporaryDirectory(prefix='fortior-contribution-install-') as temporary:
        stage=Path(temporary)/SKILL_NAME
        shutil.copytree(SOURCE,stage,symlinks=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'))
        seal(stage,skill=SKILL_NAME,source=identity)
        try:
            for dst in destinations:
                result=install_tree(stage,dst,replace=replace,protected_root=ROOT)
                if result['status']=='installed':changes.append(result)
            ensure_local_config()
        except Exception:
            for result in reversed(changes):
                dst=Path(result['destination']);backup=result.get('previous_installation_backup')
                if dst.exists():dst.rename(dst.with_name('.'+dst.name+'.failed-group-'+uuid.uuid4().hex))
                if backup:Path(backup).rename(dst)
            if previous_config is None:config.unlink(missing_ok=True)
            else:config.write_bytes(previous_config)
            raise
    return destinations

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

    # An upgrade must not switch a user's local-only/private submission mode,
    # endpoint or credentials. Defaults are copied only on first installation.

    if changed:
        config.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Fortior knowledge contribution skill")
    parser.add_argument("--target", choices=["auto", "all", "agents", "codex", "copilot", "claude", "gemini", "custom"], default="auto")
    parser.add_argument("--path", help="Custom skills directory for --target custom")
    parser.add_argument("--replace", action="store_true", help="Back up and replace this Skill and its runtime")
    parser.add_argument("--verify", type=Path, help="Verify one existing Skill directory; no writes")
    args = parser.parse_args()
    if args.verify:
        if args.replace or args.path:
            parser.error('--verify cannot be combined with installation options')
        print(json.dumps(verify(args.verify), ensure_ascii=False, indent=2))
        return

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

    # Check both destinations before starting; an initial install must not
    # silently replace an already installed runtime.
    destinations = [base.expanduser().absolute() / SKILL_NAME for base in dict.fromkeys(bases)] + [RUNTIME]
    if not args.replace and any(p.exists() for p in destinations):
        raise SystemExit('Existing Skill/runtime: rerun with --replace to retain a backup before replacement')
    install_destinations(destinations, replace=args.replace)
    installed = [base.expanduser().absolute()/SKILL_NAME for base in dict.fromkeys(bases)]
    runtime = RUNTIME
    config = HOME/'.fortior'/'knowledge-contributor.env'

    print("Installed Fortior skill:")
    for path in installed:
        print(f"  - {path}")
    print(f"Stable runtime: {runtime}")
    print(f"Submit runtime: {runtime / 'scripts' / 'submit.py'}")
    print(f"Local config: {config}")
    print("Reload/restart the host before new submissions. Repository freshness was not checked by this installer.")
    print("Default Gateway: https://fortior-knowledge-contribution-gateway.onrender.com")
    print("No GitHub/Feishu account is required to use the skill.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc))
