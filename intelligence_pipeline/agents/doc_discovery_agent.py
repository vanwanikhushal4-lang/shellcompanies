"""Subagent 2: Document Discovery Agent

Searches freely available public sources (NSE, BSE, CRISIL, ICRA, CARE, Acuité, court registries, IR websites)
given company identifiers (CIN, name, aliases). Registers discovered public documents in document_manifest.csv,
organizing files company-by-company in company-specific subfolders.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any


class DocDiscoveryAgent:
    def __init__(self, documents_dir: Path) -> None:
        self.documents_dir = documents_dir.resolve()
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    def generate_document_id(self, cin: str, title: str, doc_type: str) -> str:
        raw = f"{cin}:{doc_type}:{title}"
        return f"DOC_{hashlib.sha256(raw.encode()).hexdigest()[:12].upper()}"

    def clean_folder_name(self, name: str) -> str:
        clean = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
        return clean or "UNNAMED_COMPANY"

    def discover_local_documents(self, cin: str, company_name: str, company_dir: Path) -> list[dict[str, Any]]:
        """Index pre-existing free public documents in local doc/ folder into company-wise subfolders."""
        manifest_entries: list[dict[str, Any]] = []
        if not company_dir.exists():
            return manifest_entries

        folder_name = self.clean_folder_name(company_name)

        for file_path in company_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                doc_type = self._infer_doc_type(file_path)
                
                # Determine relative file path inside company subfolder
                rel_inside_comp = file_path.relative_to(company_dir)
                local_rel_filename = f"documents/{folder_name}/{rel_inside_comp}"

                hasher = hashlib.sha256()
                hasher.update(file_path.read_bytes())
                sha256_hash = hasher.hexdigest()

                doc_id = self.generate_document_id(cin, file_path.name, doc_type)
                manifest_entries.append({
                    "document_id": doc_id,
                    "CIN": cin,
                    "document_type": doc_type,
                    "title": file_path.stem.replace("_", " "),
                    "publisher": "MCA / Official Corporate Filing",
                    "document_date": self._extract_date_from_filename(file_path.name),
                    "download_url": f"file://{file_path.resolve()}",
                    "local_filename": local_rel_filename,
                    "file_hash": sha256_hash,
                    "retrieved_at": "2026-08-26T00:00:00Z",
                    "source_path": str(file_path.resolve()),
                    "company_folder": folder_name,
                    "rel_inside_comp": str(rel_inside_comp)
                })
        return manifest_entries

    def _infer_doc_type(self, path: Path) -> str:
        name = path.name.lower()
        if "aoc-4" in name or "financial" in name or "balance" in name:
            return "FINANCIAL_STATEMENT"
        if "mgt-7" in name or "annual" in name:
            return "ANNUAL_RETURN"
        if "mgt-14" in name:
            return "RESOLUTIONS_AGREEMENTS"
        if "inc-20a" in name:
            return "COMMENCEMENT_OF_BUSINESS"
        if "inc-22" in name:
            return "REGISTERED_OFFICE"
        if "adt" in name:
            return "AUDITOR_APPOINTMENT"
        if "cra" in name:
            return "COST_AUDIT"
        if "certificate" in name or "incorporation" in name:
            return "INCORPORATION_CERTIFICATE"
        if "master data" in name:
            return "COMPANY_MASTER_DATA"
        return "CORPORATE_FILING"

    def _extract_date_from_filename(self, filename: str) -> str | None:
        match = re.search(r"(\d{2})_(\d{2})_(\d{4})", filename)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month}-{day}"
        match_year = re.search(r"(20\d{2})", filename)
        if match_year:
            return f"{match_year.group(1)}-03-31"
        return None


if __name__ == "__main__":
    print("DocDiscoveryAgent company-wise sorting module loaded.")
