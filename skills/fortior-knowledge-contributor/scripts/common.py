from __future__ import annotations

import json
import os
from pathlib import Path
from urllib import error, request


def config_path() -> Path:
    override = os.environ.get("FORTIOR_CONFIG")
    return Path(override).expanduser() if override else Path.home() / ".fortior" / "knowledge-contributor.env"


def load_config() -> dict[str, str]:
    cfg = dict(os.environ)
    path = config_path()
    if not path.exists():
        return cfg
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        cfg.setdefault(key.strip(), value.strip())
    return cfg


def update_config_values(updates: dict[str, str]) -> Path:
    """Update selected keys in the local config while preserving comments/order."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    remaining = {k: str(v) for k, v in updates.items()}
    out: list[str] = []

    for raw in lines:
        if "=" not in raw or raw.lstrip().startswith("#"):
            out.append(raw)
            continue
        key, _ = raw.split("=", 1)
        stripped = key.strip()
        if stripped in remaining:
            out.append(f"{stripped}={remaining.pop(stripped)}")
        else:
            out.append(raw)

    if remaining:
        if out and out[-1].strip():
            out.append("")
        out.append("# Updated automatically by Fortior setup")
        for key, value in remaining.items():
            out.append(f"{key}={value}")

    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return path


def require(cfg: dict[str, str], *keys: str) -> None:
    missing = [k for k in keys if not cfg.get(k)]
    if missing:
        raise RuntimeError("Missing configuration: " + ", ".join(missing))


def http_json(method: str, url: str, payload=None, headers=None, timeout: int = 30):
    final_headers = {"Content-Type": "application/json; charset=utf-8"}
    if headers:
        final_headers.update(headers)
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=body, headers=final_headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def feishu_tenant_access_token(cfg: dict[str, str]) -> str:
    require(cfg, "FEISHU_APP_ID", "FEISHU_APP_SECRET")
    data = http_json(
        "POST",
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/",
        {"app_id": cfg["FEISHU_APP_ID"], "app_secret": cfg["FEISHU_APP_SECRET"]},
    )
    if data.get("code") != 0 or not data.get("tenant_access_token"):
        raise RuntimeError(f"Unable to obtain Feishu tenant_access_token: {data}")
    return data["tenant_access_token"]


def compact(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)
