from __future__ import annotations

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List, Optional

from .config import DbCreds
from .models import VitaRow


def _fmt_dt(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    return str(v)


def ensure_pytds() -> None:
    """Ensure python-tds is available.

    We intentionally do NOT vendor DB drivers; instead we install python-tds into
    the active environment. If missing, we print a clear error.
    """
    try:
        import pytds  # type: ignore
        return
    except Exception:
        raise RuntimeError(
            "Missing dependency 'python-tds'. Install it in your venv: "
            "pip install python-tds"
        )


def connect(creds: DbCreds):
    ensure_pytds()
    import pytds  # type: ignore

    # Optional TLS (some SQL Servers require encryption and will otherwise close the connection).
    cafile = os.environ.get("VITA_DB_CAFILE", "").strip() or None
    validate_host = os.environ.get("VITA_DB_VALIDATE_HOST", "1").strip() not in ("0", "false", "False")
    enc_login_only = os.environ.get("VITA_DB_ENC_LOGIN_ONLY", "0").strip() in ("1", "true", "True")

    return pytds.connect(
        server=creds.server,
        database=creds.database,
        user=creds.user,
        password=creds.password,
        timeout=10,
        login_timeout=10,
        cafile=cafile,
        validate_host=validate_host,
        enc_login_only=enc_login_only,
    )


def list_processes(creds: DbCreds, sn: str) -> List[str]:
    conn = connect(creds)
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT WorkStepProcessName FROM dbo.VitaTestData WHERE SerialNumber=%s ORDER BY WorkStepProcessName",
        (sn,),
    )
    vals = [r[0] for r in cur.fetchall() if r and r[0] is not None]
    cur.close(); conn.close()
    return [str(v) for v in vals]


def list_worksteps(creds: DbCreds, sn: str) -> List[str]:
    conn = connect(creds)
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT WorkStep FROM dbo.VitaTestData WHERE SerialNumber=%s ORDER BY WorkStep",
        (sn,),
    )
    vals = [r[0] for r in cur.fetchall() if r and r[0] is not None]
    cur.close(); conn.close()
    return [str(v) for v in vals]


def query_rows(
    creds: DbCreds,
    *,
    sn: str,
    process: str = "",
    process_like: str = "",
    workstep: str = "",
    limit: int = 50,
) -> List[VitaRow]:
    # SN is required; filters are optional (but can return many rows).
    where = ["SerialNumber=%s"]
    params: List[Any] = [sn]
    if process:
        where.append("WorkStepProcessName=%s"); params.append(process)
    if process_like:
        where.append("WorkStepProcessName LIKE %s"); params.append(process_like)
    if workstep:
        where.append("WorkStep=%s"); params.append(workstep)

    sql = f"""
SELECT TOP {int(limit)}
  SerialNumber, ProductName, WorkStepProcessName, WorkStep,
  TestResult, Grade, IniFileName,
  TestStartTime, TestEndTime, UploadDate,
  ResultDatFileName, ResultJsonFileName, ResultRawFileName
FROM dbo.VitaTestData
WHERE {" AND ".join(where)}
ORDER BY TestEndTime DESC, UploadDate DESC
"""

    conn = connect(creds)
    cur = conn.cursor()
    cur.execute(sql, tuple(params))
    fetched = cur.fetchall()
    cur.close(); conn.close()

    rows: List[VitaRow] = []
    for r in fetched:
        (
            serial,
            product,
            proc,
            ws,
            test_result,
            grade,
            ini,
            t0,
            t1,
            up,
            xlsx,
            js,
            zp,
        ) = r
        rows.append(
            VitaRow(
                serial=str(serial or ""),
                product=str(product or ""),
                process=str(proc or ""),
                workstep=str(ws or ""),
                test_result=str(test_result or ""),
                grade=str(grade or ""),
                program_ini=str(ini or ""),
                test_start=_fmt_dt(t0),
                test_end=_fmt_dt(t1),
                upload_date=_fmt_dt(up),
                result_xlsx=str(xlsx or ""),
                result_json=str(js or ""),
                result_zip=str(zp or ""),
            )
        )
    return rows


def pick(rows: List[VitaRow], select: str) -> List[VitaRow]:
    select = (select or "final").lower()
    if select == "all":
        return rows
    if not rows:
        return []
    if select == "final":
        return [rows[0]]
    if select == "first":
        return [rows[-1]]
    raise ValueError("select must be final|first|all")
