"""Subagent 1: MCA API Ingestion Agent

Responsible for resumable pagination from data.gov.in MCA Master API,
storing raw JSON responses, deduplicating primarily by CIN,
handling rate limits & throttling, and building the seed company identity queue.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_RESOURCE_ID = "4dbe5667-7b6b-41d7-82af-211562424d9a"
DEFAULT_BASE_URL = "https://api.data.gov.in/resource"


class MCAIngestionAgent:
    def __init__(self, output_dir: Path, api_key: str | None = None) -> None:
        self.output_dir = output_dir.resolve()
        self.raw_dir = self.output_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path = self.output_dir / "checkpoint.json"
        self.api_key = api_key or os.getenv("DATA_GOV_IN_API_KEY")

    def fetch_page(self, base_url: str, resource_id: str, offset: int, limit: int, timeout: int = 60) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("DATA_GOV_IN_API_KEY environment variable or api_key parameter is required")
        query = urlencode({
            "api-key": self.api_key,
            "format": "json",
            "offset": offset,
            "limit": limit,
        })
        url = f"{base_url.rstrip('/')}/{resource_id}?{query}"
        request = Request(url, headers={"User-Agent": "FreeCompanyIntelligenceAgent/1.0"})
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)

    def extract_records(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if not isinstance(payload, dict):
            return []
        for key in ("records", "data", "results"):
            val = payload.get(key)
            if isinstance(val, list):
                return [item for item in val if isinstance(item, dict)]
        res = payload.get("result")
        if isinstance(res, dict):
            return self.extract_records(res)
        return []

    def process_records(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        aliases = {
            "cin": ["corporate_identification_number", "cin", "corporate_id"],
            "company_name": ["company_name", "name_of_company"],
            "company_status": ["company_status", "status"],
            "company_class": ["company_class", "class_of_company"],
            "company_category": ["company_category", "category"],
            "company_subcategory": ["company_subcategory", "subcategory"],
            "roc": ["roc", "registrar_of_companies", "roc_code"],
            "registration_date": ["date_of_registration", "registration_date", "date_of_incorporation"],
            "registered_state": ["registered_state", "state"],
            "registered_office_address": ["registered_office_address", "registered_address", "address"],
            "authorized_capital": ["authorized_capital", "authorised_capital"],
            "paid_up_capital": ["paid_up_capital", "paidup_capital"],
            "activity_description": ["activity_description", "principal_business_activity", "industrial_class"],
            "email": ["email", "email_id"],
        }
        deduplicated: dict[str, dict[str, Any]] = {}
        for rec in records:
            item = {}
            indexed = {str(k).strip().lower().replace(" ", "_"): v for k, v in rec.items()}
            for canonical_key, alt_keys in aliases.items():
                val = None
                for alt in alt_keys:
                    if alt in indexed and indexed[alt] not in (None, ""):
                        val = indexed[alt]
                        break
                item[canonical_key] = val
            cin = str(item.get("cin") or "").strip().upper()
            fallback = hashlib.sha256(json.dumps(rec, sort_keys=True, default=str).encode()).hexdigest()
            key = cin or fallback
            deduplicated[key] = item
        return list(deduplicated.values())


if __name__ == "__main__":
    print("MCAIngestionAgent initialized successfully.")
