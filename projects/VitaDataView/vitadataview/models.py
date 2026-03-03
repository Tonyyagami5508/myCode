from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class VitaRow:
    serial: str
    product: str
    process: str
    workstep: str
    test_result: str
    grade: str
    program_ini: str
    test_start: Optional[str]
    test_end: Optional[str]
    upload_date: Optional[str]
    result_xlsx: str
    result_json: str
    result_zip: str
