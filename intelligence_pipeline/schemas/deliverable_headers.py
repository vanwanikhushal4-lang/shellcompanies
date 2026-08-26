"""Canonical deliverable CSV headers and schema definitions for Free Company Intelligence Pipeline."""

from __future__ import annotations

COMPANY_FACTS_HEADERS = [
    "company_id",
    "CIN",
    "field",
    "value",
    "as_of_date",
    "source_publisher",
    "source_type",
    "document_title",
    "document_date",
    "source_url",
    "source_page",
    "retrieved_at",
    "confidence",
    "reviewer_status",
    "notes"
]

RELATIONSHIPS_HEADERS = [
    "source_type",
    "source_id",
    "source_name",
    "edge_type",
    "target_type",
    "target_id",
    "target_name",
    "start_date",
    "end_date",
    "source_url",
    "source_page",
    "confidence"
]

LEGAL_EVENTS_HEADERS = [
    "CIN",
    "company_name",
    "agency_or_court",
    "action_type",
    "case_reference",
    "event_date",
    "allegation",
    "finding",
    "amount",
    "status",
    "outcome",
    "source_url",
    "source_page"
]

LABEL_EVIDENCE_HEADERS = [
    "CIN",
    "label",
    "label_status",
    "confidence",
    "reason",
    "authority",
    "document_date",
    "source_url",
    "source_page",
    "independently_verified",
    "exclude_from_features"
]

DOCUMENT_MANIFEST_HEADERS = [
    "document_id",
    "CIN",
    "document_type",
    "title",
    "publisher",
    "document_date",
    "download_url",
    "local_filename",
    "file_hash",
    "retrieved_at"
]

MISSING_FIELDS_HEADERS = [
    "company_id",
    "CIN",
    "field",
    "expected_category",
    "reason_missing",
    "retrieved_at",
    "notes"
]

CONFLICTS_HEADERS = [
    "company_id",
    "CIN",
    "field",
    "value_a",
    "source_a",
    "source_date_a",
    "value_b",
    "source_b",
    "source_date_b",
    "conflict_status",
    "resolution",
    "notes"
]
