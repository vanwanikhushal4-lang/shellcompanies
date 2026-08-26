"""Exporter module for generating the 7 canonical CSV deliverables and documents directory."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path
from typing import Any

from intelligence_pipeline.schemas.deliverable_headers import (
    COMPANY_FACTS_HEADERS,
    RELATIONSHIPS_HEADERS,
    LEGAL_EVENTS_HEADERS,
    LABEL_EVIDENCE_HEADERS,
    DOCUMENT_MANIFEST_HEADERS,
    MISSING_FIELDS_HEADERS,
    CONFLICTS_HEADERS,
)


def write_csv(file_path: Path, headers: list[str], rows: list[dict[str, Any]]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            formatted_row = {}
            for col in headers:
                val = row.get(col)
                if val is None:
                    formatted_row[col] = ""  # Recorded as null/empty in CSV
                else:
                    formatted_row[col] = str(val)
            writer.writerow(formatted_row)


def export_pilot_deliverables(
    output_dir: Path,
    facts: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    legal_events: list[dict[str, Any]],
    label_evidence: list[dict[str, Any]],
    document_manifest: list[dict[str, Any]],
    missing_fields: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
) -> None:
    output_dir = output_dir.resolve()
    docs_dir = output_dir / "documents"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write company_facts.csv
    write_csv(output_dir / "company_facts.csv", COMPANY_FACTS_HEADERS, facts)

    # 2. Write relationships.csv
    write_csv(output_dir / "relationships.csv", RELATIONSHIPS_HEADERS, relationships)

    # 3. Write legal_events.csv
    write_csv(output_dir / "legal_events.csv", LEGAL_EVENTS_HEADERS, legal_events)

    # 4. Write label_evidence.csv
    write_csv(output_dir / "label_evidence.csv", LABEL_EVIDENCE_HEADERS, label_evidence)

    # 5. Write document_manifest.csv
    write_csv(output_dir / "document_manifest.csv", DOCUMENT_MANIFEST_HEADERS, document_manifest)

    # 6. Write missing_fields.csv
    write_csv(output_dir / "missing_fields.csv", MISSING_FIELDS_HEADERS, missing_fields)

    # 7. Write conflicts.csv
    write_csv(output_dir / "conflicts.csv", CONFLICTS_HEADERS, conflicts)

    print(f"Successfully exported 7 CSV deliverables to: {output_dir}")
