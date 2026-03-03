# VitaDataView

A small CLI/API utility to query **VitaTesting** SQL Server data (`DbMaster01.dbo.VitaTestData`).

This project is designed to run on this Mac mini and **reuse the existing local credential file**:

- Default credentials file: `~/.openclaw/workspace/credentials/vita-db.json`

## Safety
- Do **NOT** commit any credentials.
- This repo intentionally ignores `.env`, `credentials/`, etc.

## Quick start (CLI)

```bash
cd projects/VitaDataView
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .

# list processes for a SN
vitadataview processes --sn DD650-100-001

# query latest record for a SN+process
vitadataview query --sn DD650-100-001 --process LTLC_Before --select final --format json
```

## DB fields (core)
The tool returns (subset):
- SerialNumber, ProductName
- WorkStepProcessName, WorkStep
- TestResult, Grade
- IniFileName
- TestStartTime, TestEndTime, UploadDate
- ResultDatFileName (xlsx), ResultJsonFileName (json), ResultRawFileName (zip)


## Web UI (local)

```bash
cd projects/VitaDataView
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e '.[web]'

# run
vitadataview-web
# open http://127.0.0.1:8899
```
