"""Subagent 4: Legal Event Agent

Parses judicial orders and regulatory actions (NCLT, NCLAT, High Courts, SEBI, ED, SFIO, IBBI),
converting official proceedings into structured legal event records (`legal_events.csv`).
STRICT RULE: Allegations and final findings MUST be kept completely separate.
"""

from __future__ import annotations

import re
from typing import Any


class LegalEventAgent:
    def __init__(self) -> None:
        pass

    def parse_legal_document(self, text: str, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse legal proceedings text into legal_events.csv schema entries."""
        events: list[dict[str, Any]] = []

        cin = metadata.get("CIN")
        company_name = metadata.get("company_name", "UNKNOWN COMPANY")
        agency = metadata.get("agency_or_court", "NCLT / Court")

        # Detect regulatory/court keywords
        is_legal = any(kw in text.lower() for kw in [
            "nclt", "nclat", "high court", "sebi", "enforcement directorate",
            "sfio", "ibbi", "section 7", "section 9", "cirp", "strike off", "allegation"
        ])

        if not is_legal and not metadata.get("force_legal"):
            return events

        # Determine action type and status
        action_type = "REGULATORY_PROCEEDING"
        procedural_status = "PENDING"
        if "insolvency" in text.lower() or "cirp" in text.lower() or "nclt" in text.lower():
            action_type = "INSOLVENCY_PROCEEDING"
        elif "strike off" in text.lower() or "striked off" in text.lower():
            action_type = "STRIKE_OFF_NOTICE"
        elif "sebi" in text.lower():
            action_type = "SEBI_ORDER"
        elif "enforcement" in text.lower() or "ed" in text.lower():
            action_type = "ED_INVESTIGATION"

        # Extract allegation vs finding
        allegation = None
        finding = None
        outcome = "UNDER_REVIEW"

        allegation_match = re.search(r"(?:alleged|allegation|charge|contention)[:\s]*([^\.\n]+)", text, re.IGNORECASE)
        if allegation_match:
            allegation = allegation_match.group(1).strip()

        finding_match = re.search(r"(?:held|finding|concluded|ordered|adjudicated)[:\s]*([^\.\n]+)", text, re.IGNORECASE)
        if finding_match:
            finding = finding_match.group(1).strip()
            procedural_status = "FINAL_ORDER"
            outcome = "ADJUDICATED"

        events.append({
            "CIN": cin,
            "company_name": company_name,
            "agency_or_court": agency,
            "action_type": action_type,
            "case_reference": metadata.get("case_reference", "REF-" + (cin[:10] if cin else "0000")),
            "event_date": metadata.get("document_date", "2026-01-01"),
            "allegation": allegation,
            "finding": finding,
            "amount": metadata.get("amount"),
            "status": procedural_status,
            "outcome": outcome,
            "source_url": metadata.get("source_url"),
            "source_page": metadata.get("source_page", "1")
        })

        return events


if __name__ == "__main__":
    print("LegalEventAgent initialized successfully.")
