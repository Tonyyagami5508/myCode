from __future__ import annotations

import html
import os
from dataclasses import asdict
from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from .config import load_creds
from .db import pick, query_rows

APP_TITLE = "VitaDataView"
MAX_LIMIT = 1000

app = FastAPI(title=APP_TITLE)


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _page(*, body: str, msg: str = "") -> str:
    # DataTables via CDN (good enough for internal tool)
    return f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{_esc(APP_TITLE)}</title>
  <link rel=\"stylesheet\" href=\"https://cdn.datatables.net/1.13.8/css/jquery.dataTables.min.css\" />
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; }}
    .row {{ display:flex; gap:12px; flex-wrap:wrap; align-items:flex-end; }}
    label {{ display:block; font-size: 12px; color:#333; margin-bottom:4px; }}
    input, select {{ padding:8px; min-width: 240px; }}
    button {{ padding: 10px 14px; cursor:pointer; }}
    .hint {{ color:#666; font-size:12px; margin-top:8px; }}
    .msg {{ margin: 12px 0; color:#b00; white-space: pre-wrap; }}
    table.dataTable thead th {{ white-space: nowrap; }}
  </style>
</head>
<body>
  <h2>{_esc(APP_TITLE)}</h2>
  <div class=\"msg\">{_esc(msg) if msg else ''}</div>

  <form method=\"get\" action=\"/\">
    <div class=\"row\">
      <div>
        <label>SN (SerialNumber) - required</label>
        <input name=\"sn\" value=\"{_esc(os.environ.get('VITADV_LAST_SN',''))}\" placeholder=\"e.g. DD650-100-001\" required />
      </div>
      <div>
        <label>WorkStep / ProcessName (fuzzy LIKE) - optional</label>
        <input name=\"workstep_like\" value=\"\" placeholder=\"e.g. LTLC\" />
      </div>
      <div>
        <label>Select</label>
        <select name=\"select\">
          <option value=\"final\">final (latest)</option>
          <option value=\"first\">first (earliest)</option>
          <option value=\"all\">all</option>
        </select>
      </div>
      <div>
        <label>Limit (max {MAX_LIMIT})</label>
        <input name=\"limit\" type=\"number\" value=\"50\" min=\"1\" max=\"{MAX_LIMIT}\" />
      </div>
      <div>
        <button type=\"submit\">Query</button>
      </div>
    </div>
    <div class=\"hint\">
      Notes: results are capped at {MAX_LIMIT} rows to avoid blowing up the UI.
    </div>
  </form>

  {body}

  <script src=\"https://code.jquery.com/jquery-3.7.1.min.js\"></script>
  <script src=\"https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js\"></script>
  <script>
    $(function() {{
      const t = $('#results');
      if (t.length) t.DataTable({{ pageLength: 25, lengthMenu: [10, 25, 50, 100], order: [] }});
    }});
  </script>
</body>
</html>"""


def _table(rows: List[dict]) -> str:
    if not rows:
        return "<p>(no rows)</p>"

    cols = [
        "serial",
        "product",
        "process",
        "workstep",
        "test_result",
        "grade",
        "test_end",
        "upload_date",
        "program_ini",
        "result_xlsx",
        "result_json",
        "result_zip",
    ]

    thead = "".join(f"<th>{_esc(c)}</th>" for c in cols)
    tbody_parts = []
    for r in rows:
        tds = "".join(f"<td>{_esc(r.get(c,''))}</td>" for c in cols)
        tbody_parts.append(f"<tr>{tds}</tr>")
    tbody = "".join(tbody_parts)

    return f"""
<table id=\"results\" class=\"display\" style=\"width:100%\">
  <thead><tr>{thead}</tr></thead>
  <tbody>{tbody}</tbody>
</table>
"""


@app.get("/", response_class=HTMLResponse)
def home(
    sn: Optional[str] = Query(default=None),
    workstep_like: str = Query(default=""),
    select: str = Query(default="final"),
    limit: int = Query(default=50),
):
    if not sn:
        return _page(body="", msg="")

    limit = max(1, min(int(limit or 50), MAX_LIMIT))

    try:
        creds = load_creds()
        process_like = ""
        if workstep_like.strip():
            process_like = f"%{workstep_like.strip()}%"

        rows = query_rows(creds, sn=sn.strip(), process_like=process_like, limit=limit)
        rows = pick(rows, select)
        dict_rows = [asdict(r) for r in rows]

        msg = ""
        if select == "all" and len(dict_rows) >= limit:
            msg = f"Showing first {limit} rows (cap). Refine filters if needed."

        # store last SN for convenience (best-effort)
        os.environ["VITADV_LAST_SN"] = sn.strip()

        return _page(body=_table(dict_rows), msg=msg)
    except Exception as e:
        return _page(body="", msg=f"ERROR: {e}")


def main() -> None:
    # For 'vitadataview-web'
    import uvicorn

    uvicorn.run("vitadataview.webapp:app", host="127.0.0.1", port=int(os.environ.get("VITADV_PORT", "8899")), reload=False)
