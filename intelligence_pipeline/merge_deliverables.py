"""Consolidate pilot_25 and batch_50 deliverables into outputs/combined_75."""

from __future__ import annotations

import csv
import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

PILOT_25_DIR = ROOT_DIR / "outputs" / "pilot_25"
BATCH_50_DIR = ROOT_DIR / "outputs" / "batch_50"
COMBINED_DIR = ROOT_DIR / "outputs" / "combined_75"
COMBINED_DOCS = COMBINED_DIR / "documents"


def merge_csv(filename: str, headers: list[str]) -> list[dict[str, str]]:
    rows = []
    seen = set()

    for d in [PILOT_25_DIR, BATCH_50_DIR]:
        path = d / filename
        if path.exists():
            with path.open(encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    raw_tuple = tuple(r.get(h, "") for h in headers[:4])
                    if raw_tuple not in seen:
                        rows.append(r)
                        seen.add(raw_tuple)
    return rows


def main() -> None:
    COMBINED_DIR.mkdir(parents=True, exist_ok=True)
    COMBINED_DOCS.mkdir(parents=True, exist_ok=True)

    # 1. Copy document subfolders from pilot_25 and batch_50 into combined_75/documents/
    for src_docs in [PILOT_25_DIR / "documents", BATCH_50_DIR / "documents"]:
        if src_docs.exists():
            for comp_dir in src_docs.iterdir():
                if comp_dir.is_dir() and not comp_dir.name.startswith("."):
                    target_dir = COMBINED_DOCS / comp_dir.name
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    shutil.copytree(comp_dir, target_dir)

    # 2. Merge CSV files
    from intelligence_pipeline.schemas.deliverable_headers import (
        COMPANY_FACTS_HEADERS,
        RELATIONSHIPS_HEADERS,
        LEGAL_EVENTS_HEADERS,
        LABEL_EVIDENCE_HEADERS,
        DOCUMENT_MANIFEST_HEADERS,
        MISSING_FIELDS_HEADERS,
        CONFLICTS_HEADERS,
    )
    from intelligence_pipeline.export_deliverables import write_csv

    write_csv(COMBINED_DIR / "company_facts.csv", COMPANY_FACTS_HEADERS, merge_csv("company_facts.csv", COMPANY_FACTS_HEADERS))
    write_csv(COMBINED_DIR / "relationships.csv", RELATIONSHIPS_HEADERS, merge_csv("relationships.csv", RELATIONSHIPS_HEADERS))
    write_csv(COMBINED_DIR / "legal_events.csv", LEGAL_EVENTS_HEADERS, merge_csv("legal_events.csv", LEGAL_EVENTS_HEADERS))
    write_csv(COMBINED_DIR / "label_evidence.csv", LABEL_EVIDENCE_HEADERS, merge_csv("label_evidence.csv", LABEL_EVIDENCE_HEADERS))
    write_csv(COMBINED_DIR / "document_manifest.csv", DOCUMENT_MANIFEST_HEADERS, merge_csv("document_manifest.csv", DOCUMENT_MANIFEST_HEADERS))
    write_csv(COMBINED_DIR / "missing_fields.csv", MISSING_FIELDS_HEADERS, merge_csv("missing_fields.csv", MISSING_FIELDS_HEADERS))
    write_csv(COMBINED_DIR / "conflicts.csv", CONFLICTS_HEADERS, merge_csv("conflicts.csv", CONFLICTS_HEADERS))

    print(f"Successfully generated consolidated 75-company dataset at: {COMBINED_DIR}")


if __name__ == "__main__":
    main()
