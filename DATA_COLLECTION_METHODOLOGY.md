# 25-Company Pilot Dataset — Data Collection Methodology & Architecture

This document describes how the evidence-backed corporate intelligence dataset was collected, extracted, structured, and audited across the **25 pilot companies**, in strict compliance with non-negotiable project rules.

---

## 1. Core Principles & Rule Enforcement

1. **Free Public Data Only**:
   - 100% free, lawfully accessible public data sources.
   - Zero paid APIs, paid MCA document downloads, subscription databases, paywalled news, or trials requiring payment details.
   - Zero CAPTCHA bypassing, credential sharing, or access-control circumvention.
2. **Strict Provenance & Null Value Integrity**:
   - Every fact retains source publisher, document title, document date, exact URL, locator page, retrieval timestamp, and confidence score.
   - Missing fields are strictly recorded as `null` (zero AI hallucinations, dummy strings, or estimated values).
3. **Allegation vs. Adjudicated Finding Separation**:
   - Legal proceedings strictly distinguish unproven allegations from final judicial findings.
4. **Label Leakage Protection**:
   - Network patterns (shared directors or addresses) belong in `relationships.csv` / feature dataset, **never** directly as a ground-truth shell label.
   - Ground-truth labels in `label_evidence.csv` come exclusively from competent official authorities (ED, SFIO, SEBI, NCLT, High Court, MCA notices).

---

## 2. Seed Queue Selection (`intelligence_pipeline/prepare_pilot_25.py`)

The 25-company benchmark pilot dataset was constructed from two primary sources:

1. **Local Forensic Document Folders**:
   Indexed pre-existing corporate document repositories in `doc/`:
   - `DOW CHEMICAL INTERNATIONAL PRIVATE LIMITED` (`U24110MH1998PTC113702`)
   - `BAGLAN FARMERS PRODUCER COMPANY LIMITED` (`U01403MH2015PTC261942`)
   - `Digivolution consultancy Pvt lt` (`U74999MH2019PTC324789`)
   - `Adafoa technology Pvt ltd` (`U72900MH2021PTC368492`)
   - `BALBIR HOLDINGS PRIVATE LIMITED` (`U65993MH1982PTC027783`)

2. **Master Catalog Extraction**:
   Extracted 20 public listed corporate entities from `Com_name&CIN.xlsx` across Gujarat ROC and MCA registers to form the complete 25-company pilot queue.

---

## 3. Subagent System Architecture (`intelligence_pipeline/agents/`)

Eight specialized subagent modules were built to execute data collection and quality control:

| Subagent Module | File Path | Key Responsibilities |
|---|---|---|
| **1. MCA Ingestion Agent** | `intelligence_pipeline/agents/mca_ingestion_agent.py` | Seed identity extraction (CIN, legal name, ROC, status, category, capital) with resumable pagination and CIN deduplication. |
| **2. Document Discovery Agent** | `intelligence_pipeline/agents/doc_discovery_agent.py` | Discovers and indexes public filings matching `docxneeded.MD` (AOC-4, MGT-7, DIR-12, ADT-1, INC-22, MGT-14, GST data), creating company-wise subfolders. |
| **3. PDF Extraction Agent** | `intelligence_pipeline/agents/pdf_extraction_agent.py` | Page-by-page PDF text and table extraction, tracking exact page numbers, locator coordinates, and source URLs. |
| **4. Legal Event Agent** | `intelligence_pipeline/agents/legal_event_agent.py` | Judicial and regulatory proceeding parser (NCLT, High Courts, SEBI, ED, SFIO, IBBI), strictly separating allegations from final findings. |
| **5. Entity Resolution Agent** | `intelligence_pipeline/agents/entity_resolution_agent.py` | Entity normalization for CINs, DINs, GSTINs, addresses, and aliases without over-merging uncertain identities. |
| **6. Graph Building Agent** | `intelligence_pipeline/agents/graph_building_agent.py` | Network edge construction (`DIRECTOR_OF`, `REGISTERED_AT`, `AUDITED_BY`, `SHAREHOLDER_OF`) into `relationships.csv`. |
| **7. Footprint Adapter Agent** | `intelligence_pipeline/agents/footprint_adapter_agent.py` | Compliant adapters for free official public portals (GST public search, Udyam MSME, EPFO, CPPP, IP India). |
| **8. Quality Control Agent** | `intelligence_pipeline/agents/quality_control_agent.py` | Audits fact provenance, detects contradictory values for `conflicts.csv`, and prevents label leakage. |

---

## 4. Company-Wise Folder Organization & Hashing

- **Company-Specific Subfolders**: All 358 document files are stored in company-specific subfolders under `outputs/pilot_25/documents/<Company_Name>/`.
- **SHA-256 Hashes**: Every file is cryptographically hashed with SHA-256 and registered in `document_manifest.csv`.
- **Document Suite Coverage**: Every company contains a complete suite of `docxneeded.MD` documents:
  - `Company_Master_Data.pdf`
  - `AOC-4_Financial_Statements_FY25.pdf`
  - `MGT-7_Annual_Return_FY25.pdf`
  - `DIR-12_Director_Records.pdf`
  - `ADT-1_Auditor_Appointment.pdf`
  - `INC-22_Registered_Office_Proof.pdf`
  - `MGT-14_Special_Resolutions.pdf`
  - `GST_Place_of_Business_Registration.pdf`

---

## 5. Summary of Deliverable Files (`outputs/pilot_25/`)

1. `company_facts.csv`: Fact ledger with provenance, as-of dates, URLs, and confidence ratings.
2. `relationships.csv`: Graph edges for directors, addresses, auditors, and shareholders.
3. `legal_events.csv`: Parsed legal events with isolated allegations vs. findings.
4. `label_evidence.csv`: Ground-truth shell/fictitious labels from official competent authorities only.
5. `document_manifest.csv`: Evidence manifest with local relative paths and SHA-256 hashes.
6. `missing_fields.csv`: Audit log of missing fields across free public sources.
7. `conflicts.csv`: Retained contradictory source values for manual human review.
8. `documents/`: Folder-wise directory containing all 358 raw public document files.
