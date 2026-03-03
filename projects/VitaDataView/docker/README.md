# VitaDataView in Docker (Sandbox)

This runs the web UI **inside a container** (good when macOS pip/network is flaky).

## Build

```bash
cd projects/VitaDataView
docker build -t vitadataview:local -f docker/Dockerfile .
```

## Run

Mount only the Vita DB creds file as read-only:

```bash
docker run --rm -it \
  -p 8899:8899 \
  -e VITA_DB_CREDS=/creds/vita-db.json \
  -v ~/.openclaw/workspace/credentials:/creds:ro \
  vitadataview:local
```

Then open:
- http://127.0.0.1:8899

Notes:
- Results are capped at **1000** rows.
- The container needs network access to reach the SQL Server (192.168.31.223).
