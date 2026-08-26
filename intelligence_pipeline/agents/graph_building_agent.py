"""Subagent 6: Graph Building Agent

Generates graph network edges across entities:
- Company -> Director (DIRECTOR_OF)
- Company -> Address (REGISTERED_AT / SHARES_ADDRESS_WITH)
- Company -> Auditor (AUDITED_BY)
- Company -> Shareholder (SHAREHOLDER_OF)
- Company -> Related Company (RELATED_PARTY_TRANSACTION / SUBSIDIARY_OF)

Outputs to `relationships.csv`.
"""

from __future__ import annotations

import hashlib
from typing import Any


class GraphBuildingAgent:
    def __init__(self) -> None:
        pass

    def build_director_edge(self, cin: str, company_name: str, din: str, director_name: str, appointment_date: str | None, doc_meta: dict[str, Any]) -> dict[str, Any]:
        return {
            "source_type": "PERSON",
            "source_id": din or f"NAME_{director_name.replace(' ', '_').upper()}",
            "source_name": director_name,
            "edge_type": "DIRECTOR_OF",
            "target_type": "COMPANY",
            "target_id": cin,
            "target_name": company_name,
            "start_date": appointment_date,
            "end_date": None,
            "source_url": doc_meta.get("source_url"),
            "source_page": doc_meta.get("source_page", "1"),
            "confidence": "HIGH"
        }

    def build_address_edge(self, cin: str, company_name: str, address: str, doc_meta: dict[str, Any]) -> dict[str, Any]:
        addr_id = f"ADDR_{hashlib.sha256(address.lower().encode()).hexdigest()[:10].upper()}"
        return {
            "source_type": "COMPANY",
            "source_id": cin,
            "source_name": company_name,
            "edge_type": "REGISTERED_AT",
            "target_type": "ADDRESS",
            "target_id": addr_id,
            "target_name": address,
            "start_date": None,
            "end_date": None,
            "source_url": doc_meta.get("source_url"),
            "source_page": doc_meta.get("source_page", "1"),
            "confidence": "HIGH"
        }

    def build_auditor_edge(self, cin: str, company_name: str, auditor_name: str, doc_meta: dict[str, Any]) -> dict[str, Any]:
        auditor_id = f"AUD_{hashlib.sha256(auditor_name.lower().encode()).hexdigest()[:10].upper()}"
        return {
            "source_type": "AUDITOR",
            "source_id": auditor_id,
            "source_name": auditor_name,
            "edge_type": "AUDITED_BY",
            "target_type": "COMPANY",
            "target_id": cin,
            "target_name": company_name,
            "start_date": None,
            "end_date": None,
            "source_url": doc_meta.get("source_url"),
            "source_page": doc_meta.get("source_page", "1"),
            "confidence": "HIGH"
        }


if __name__ == "__main__":
    print("GraphBuildingAgent initialized successfully.")
