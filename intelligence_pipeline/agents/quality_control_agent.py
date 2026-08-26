"""Subagent 8: Quality Control Agent

Enforces quality assurance, provenance verification, label leakage checks,
and conflict detection across extracted dataset records.

Generates:
- `missing_fields.csv`
- `conflicts.csv`
- Validation reports
"""

from __future__ import annotations

import re
from typing import Any


class QualityControlAgent:
    def __init__(self) -> None:
        pass

    def validate_fact(self, fact: dict[str, Any]) -> list[str]:
        errors: list[str] = []

        # Check required fields
        if not fact.get("field"):
            errors.append("Missing field name")
        if fact.get("value") in ("N/A", "None", "unknown", "UNKNOWN", "undefined"):
            errors.append("Forbidden dummy string in value (must be null/None)")

        # Check provenance
        if not fact.get("source_publisher") and not fact.get("source_url"):
            errors.append("Missing provenance (source_publisher or source_url required)")

        # Check CIN format if present
        cin = fact.get("CIN")
        if cin:
            cin_pattern = r"^[UL]\d{5}[A-Z]{2}\d{4}(PLC|PTC|SGC|FLC|ULL|NPL)\d{6}$"
            if not re.match(cin_pattern, str(cin).strip().upper()):
                errors.append(f"Malformed CIN: {cin}")

        return errors

    def audit_label_evidence(self, label_row: dict[str, Any]) -> list[str]:
        errors: list[str] = []

        # Ensure ground truth comes ONLY from an official competent authority
        authority = str(label_row.get("authority") or "").lower()
        official_keywords = ["court", "ed", "sfio", "sebi", "rbi", "mca", "roc", "high court", "nclt", "cbi"]

        if not any(kw in authority for kw in official_keywords):
            errors.append(f"Label authority '{authority}' is not a recognized official competent source")

        # Label leakage check: Network signals must not be ground-truth shell labels
        reason = str(label_row.get("reason") or "").lower()
        if "shared address" in reason or "common director" in reason:
            errors.append("LABEL LEAKAGE DETECTED: Network pattern used as ground-truth shell label reason")

        return errors

    def detect_conflicts(self, facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Detect contradictory values across independent sources for the same field."""
        conflicts: list[dict[str, Any]] = []
        field_map: dict[tuple[str, str], list[dict[str, Any]]] = {}

        for fact in facts:
            key = (fact.get("CIN", ""), fact.get("field", ""))
            if key not in field_map:
                field_map[key] = []
            field_map[key].append(fact)

        for (cin, field), fact_list in field_map.items():
            if len(fact_list) > 1:
                # Compare unique non-null values
                values = {f.get("value") for f in fact_list if f.get("value")}
                if len(values) > 1:
                    f_a = fact_list[0]
                    f_b = fact_list[1]
                    conflicts.append({
                        "company_id": f_a.get("company_id", f"COMP_{cin}"),
                        "CIN": cin,
                        "field": field,
                        "value_a": f_a.get("value"),
                        "source_a": f_a.get("source_publisher"),
                        "source_date_a": f_a.get("document_date"),
                        "value_b": f_b.get("value"),
                        "source_b": f_b.get("source_publisher"),
                        "source_date_b": f_b.get("document_date"),
                        "conflict_status": "UNRESOLVED",
                        "resolution": "RETAINED_FOR_REVIEW",
                        "notes": "Contradictory values found across sources"
                    })

        return conflicts


if __name__ == "__main__":
    print("QualityControlAgent initialized successfully.")
