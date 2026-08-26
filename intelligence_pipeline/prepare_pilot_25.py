"""Prepare 25-company benchmark pilot queue combining local doc/ entries and Com_name&CIN.xlsx using openpyxl."""

from __future__ import annotations

import json
from pathlib import Path
import openpyxl

ROOT_DIR = Path(__file__).resolve().parent.parent
DOC_DIR = ROOT_DIR / "doc"
EXCEL_PATH = ROOT_DIR / "Com_name&CIN.xlsx"
OUTPUT_SEED = ROOT_DIR / "intelligence_pipeline" / "config" / "seed_pilot_25.json"


def main() -> None:
    seed_companies = []

    # 1. Add companies from local doc/ directory
    doc_companies = [
        {"name": "Adafoa technology Pvt ltd", "cin": "U72900MH2021PTC368492", "status": "Active"},
        {"name": "BAGLAN FARMERS PRODUCER COMPANY LIMITED-20260803T053634Z-1-001", "cin": "U01403MH2015PTC261942", "status": "Active"},
        {"name": "BALBIR HOLDINGS PRIVATE LIMITED", "cin": "U65993MH1982PTC027783", "status": "Active"},
        {"name": "DOW CHEMICAL INTERNATIONAL PRIVATE LIMITED", "cin": "U24110MH1998PTC113702", "status": "Active"},
        {"name": "Digivolution consultancy Pvt lt", "cin": "U74999MH2019PTC324789", "status": "Active"},
    ]

    for comp in doc_companies:
        seed_companies.append({
            "company_id": f"COMP_{comp['cin']}",
            "cin": comp["cin"],
            "company_name": comp["name"],
            "company_status": comp["status"],
            "has_local_docs": True,
            "doc_dir": str(DOC_DIR / comp["name"])
        })

    # 2. Extract additional companies from Com_name&CIN.xlsx to make 25 companies
    if EXCEL_PATH.exists():
        wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True)
        sheet = wb.active
        existing_cins = {c["cin"] for c in seed_companies}

        cin_idx = 0
        name_idx = 1
        header_found = False

        for row in sheet.iter_rows(values_only=True):
            if not row or not any(row):
                continue
            if not header_found:
                row_str = [str(cell).lower() if cell else "" for cell in row]
                for idx, cell in enumerate(row_str):
                    if "cin" in cell:
                        cin_idx = idx
                    if "name" in cell:
                        name_idx = idx
                header_found = True
                continue

            cin_val = str(row[cin_idx]).strip().upper() if len(row) > cin_idx and row[cin_idx] else ""
            name_val = str(row[name_idx]).strip() if len(row) > name_idx and row[name_idx] else ""

            if cin_val and cin_val not in existing_cins and len(cin_val) == 21:
                seed_companies.append({
                    "company_id": f"COMP_{cin_val}",
                    "cin": cin_val,
                    "company_name": name_val or f"COMPANY {cin_val}",
                    "company_status": "Active",
                    "has_local_docs": False,
                    "doc_dir": None
                })
                existing_cins.add(cin_val)

            if len(seed_companies) >= 25:
                break

    OUTPUT_SEED.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SEED.write_text(json.dumps(seed_companies, indent=2), encoding="utf-8")
    print(f"Successfully generated 25-company benchmark pilot queue at: {OUTPUT_SEED}")


if __name__ == "__main__":
    main()
