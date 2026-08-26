"""Extract 50 new companies from Com_name&CIN.xlsx excluding the pilot 25 companies."""

from __future__ import annotations

import json
from pathlib import Path
import openpyxl

ROOT_DIR = Path(__file__).resolve().parent.parent
EXCEL_PATH = ROOT_DIR / "Com_name&CIN.xlsx"
PILOT_25_PATH = ROOT_DIR / "intelligence_pipeline" / "config" / "seed_pilot_25.json"
OUTPUT_SEED_50 = ROOT_DIR / "intelligence_pipeline" / "config" / "seed_batch_50.json"


def main() -> None:
    # 1. Load pilot 25 CINs to exclude them
    pilot_cins = set()
    if PILOT_25_PATH.exists():
        pilot_data = json.loads(PILOT_25_PATH.read_text(encoding="utf-8"))
        for item in pilot_data:
            pilot_cins.add(item["cin"].strip().upper())

    print(f"Loaded {len(pilot_cins)} pilot 25 CINs to exclude.")

    # 2. Parse Com_name&CIN.xlsx for 50 new companies
    wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True)
    sheet = wb.active

    cin_idx = 0
    name_idx = 1
    header_found = False

    batch_50_companies = []
    seen_cins = set(pilot_cins)

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

        if cin_val and cin_val not in seen_cins and len(cin_val) == 21:
            batch_50_companies.append({
                "company_id": f"COMP_{cin_val}",
                "cin": cin_val,
                "company_name": name_val or f"COMPANY {cin_val}",
                "company_status": "Active",
                "has_local_docs": False,
                "doc_dir": None
            })
            seen_cins.add(cin_val)

        if len(batch_50_companies) >= 50:
            break

    OUTPUT_SEED_50.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SEED_50.write_text(json.dumps(batch_50_companies, indent=2), encoding="utf-8")
    print(f"Successfully generated seed batch of {len(batch_50_companies)} new companies at: {OUTPUT_SEED_50}")


if __name__ == "__main__":
    main()
