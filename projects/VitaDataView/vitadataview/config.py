from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DbCreds:
    server: str
    database: str
    user: str
    password: str


def default_creds_path() -> Path:
    # Prefer env override.
    p = os.environ.get("VITA_DB_CREDS")
    if p:
        return Path(p).expanduser()

    ws = Path(os.environ.get("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw" / "workspace")))
    return ws / "credentials" / "vita-db.json"


def load_creds() -> DbCreds:
    p = default_creds_path()
    if not p.exists():
        raise FileNotFoundError(f"Missing credentials file: {p}")
    obj = json.loads(p.read_text(encoding="utf-8"))
    server = str(obj.get("server") or "").strip()
    database = str(obj.get("database") or "DbMaster01").strip()
    user = str(obj.get("user") or "").strip()
    password = str(obj.get("password") or "").strip()
    if not (server and user and password):
        raise ValueError(f"Invalid creds file (need server/user/password): {p}")
    return DbCreds(server=server, database=database, user=user, password=password)
