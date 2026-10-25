"""Local-only package identity and recoverable manual install. No network/model calls.

Content digests identify bytes; they do not establish approval or remote freshness.
Vendored identically in ContributionSkills; cross-repository tests pin this contract.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

IDENTITY = 'package-identity.json'
RECEIPT = 'manual-install.json'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def file_map(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('package root must be a real directory')
    files = {}
    for directory, names, leaves in os.walk(root, followlinks=False):
        for name in names + leaves:
            p = Path(directory) / name
            if p.is_symlink():
                raise ValueError('package symlink rejected: ' + str(p.relative_to(root)))
        names[:] = sorted(n for n in names if n not in ('__pycache__', '.git'))
        for name in sorted(leaves):
            p = Path(directory) / name
            relative = p.relative_to(root).as_posix()
            if relative in (IDENTITY, RECEIPT) or name.endswith(('.pyc', '.pyo')):
                continue
            if name in ('.env', 'config.env', 'credentials.json'):
                raise ValueError('local credential/config file must not be packaged: ' + relative)
            files[relative] = hashlib.sha256(p.read_bytes()).hexdigest()
    if 'SKILL.md' not in files:
        raise ValueError('package requires SKILL.md')
    return dict(sorted(files.items()))


def source_identity(root):
    root = Path(root).resolve()
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args],
                                       stderr=subprocess.DEVNULL, text=True).strip()
    try:
        if Path(git('rev-parse', '--show-toplevel')).resolve() != root:
            raise ValueError('not the repository root')
        return {'commit': git('rev-parse', 'HEAD'),
                'dirty': bool(git('status', '--porcelain', '--untracked-files=normal')),
                'origin': 'local_git_checkout', 'remote_freshness': 'not_checked'}
    except (OSError, ValueError, subprocess.CalledProcessError):
        return {'commit': 'unknown', 'dirty': None, 'origin': 'local_directory',
                'remote_freshness': 'not_checked'}


def seal(root, *, skill, source, pool=None):
    root = Path(root)
    files = file_map(root)
    value = {'schema_version': 'fortior.local-package.v1', 'skill': skill,
             'content_sha256': digest(files), 'files': files,
             'source': source, 'review_pool': pool,
             'update_policy': 'manual_local_repository',
             'freshness': 'not_checked', 'approval_inferred': False}
    value['identity_sha256'] = digest(value)
    (root / IDENTITY).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return verify(root)


def verify(root):
    root = Path(root)
    # Reject links before opening even the identity file.
    files = file_map(root)
    value = json.loads((root / IDENTITY).read_text(encoding='utf-8'))
    if value.get('schema_version') != 'fortior.local-package.v1':
        raise ValueError('unsupported local package identity')
    claimed_identity = value.get('identity_sha256')
    if claimed_identity != digest({k: v for k, v in value.items() if k != 'identity_sha256'}):
        raise ValueError('local identity metadata mismatch')
    if value.get('files') != files or value.get('content_sha256') != digest(files):
        raise ValueError('local package file/content mismatch')
    manifest = root / 'references/manifest.json'
    if value.get('review_pool') is not None:
        if not manifest.is_file() or json.loads(manifest.read_text(encoding='utf-8')) != value['review_pool']:
            raise ValueError('review pool differs from sealed identity')
    return value


def install_tree(source, destination, *, replace=False, protected_root=None):
    if Path(source).is_symlink():
        raise ValueError('source package symlink is not supported')
    source = Path(source).resolve()
    raw_destination = Path(destination).expanduser().absolute()
    for part in (raw_destination, *raw_destination.parents):
        if part.is_symlink():
            raise ValueError('installation through symlink is not supported')
    destination = raw_destination.resolve()
    for protected in (source, Path(protected_root).resolve() if protected_root else source):
        if destination == protected or destination in protected.parents or protected in destination.parents:
            raise ValueError('installation must not overlap the source repository/package')
    identity = verify(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock = destination.with_name('.' + destination.name + '.install-lock')
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise ValueError('installation lock exists; inspect it, do not run concurrent installs') from exc
    stage = None
    backup = None
    try:
        if destination.exists():
            if not destination.is_dir() or not (destination / 'SKILL.md').is_file():
                raise ValueError('refuse to replace a directory that is not a Skill')
            if not replace:
                raise ValueError('existing installation requires --replace; a backup is retained')
            # Reinstalling identical bytes is a no-op, not another backup.
            try:
                old = verify(destination)
                if old == identity:
                    return {'status': 'unchanged', 'destination': str(destination), 'identity': identity}
            except (ValueError, OSError, json.JSONDecodeError):
                pass
        stage = Path(tempfile.mkdtemp(prefix='.' + destination.name + '.stage-', dir=destination.parent))
        shutil.copytree(source, stage, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
        verify(stage)
        receipt = {'schema_version': 'fortior.manual-install.v1',
                   'installed_at': datetime.now(timezone.utc).isoformat(),
                   'destination': str(destination), 'package_content_sha256': identity['content_sha256'],
                   'package_identity_sha256': identity['identity_sha256'],
                   'source': identity['source'], 'review_pool': identity['review_pool'],
                   'remote_freshness': 'not_checked', 'host_reload_required': True}
        if destination.exists():
            backup = destination.with_name('.' + destination.name + '.backup-' + uuid4().hex)
            receipt['previous_installation_backup'] = str(backup)
        (stage / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if backup:
            destination.rename(backup)
        try:
            stage.rename(destination)
            stage = None
            verify(destination)
        except Exception:
            if destination.exists():
                failed = destination.with_name('.' + destination.name + '.failed-' + uuid4().hex)
                destination.rename(failed)
            if backup and backup.exists():
                backup.rename(destination)
            raise
        return {'status': 'installed', **receipt, 'identity': identity}
    finally:
        if stage and stage.exists():
            shutil.rmtree(stage)
        lock.rmdir()


def describe(root):
    """Verify installed bytes, then return a bounded, non-secret run identity."""
    root = Path(root)
    if not (root / IDENTITY).exists():
        return {'status': 'legacy_unsealed', 'path': str(root.resolve()),
                'update_policy': 'manual_local_repository', 'remote_freshness': 'not_checked'}
    identity = verify(root)
    members = root / 'references/pool-members.json'
    return {'status': 'verified_local_bytes', 'path': str(root.resolve()),
            'skill': identity['skill'], 'source': identity['source'],
            'content_sha256': identity['content_sha256'], 'identity_sha256': identity['identity_sha256'],
            'review_pool': identity['review_pool'],
            'pool_members': json.loads(members.read_text(encoding='utf-8')) if members.is_file() else None,
            'update_policy': 'manual_local_repository', 'remote_freshness': 'not_checked',
            'actual_host_skill_read_verified': False}
