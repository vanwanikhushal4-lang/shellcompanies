#!/usr/bin/env python3
"""Resumable free data.gov.in MCA Company Master Data collector."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_RESOURCE_ID = "4dbe5667-7b6b-41d7-82af-211562424d9a"
DEFAULT_BASE_URL = "https://api.data.gov.in/resource"


def normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def canonical_value(record: dict[str, Any], aliases: list[str]) -> Any:
    indexed = {normalized_key(str(key)): value for key, value in record.items()}
    for alias in aliases:
        value = indexed.get(normalized_key(alias))
        if value not in (None, ""):
            return value
    return None


def extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("records", "data", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    result = payload.get("result")
    if isinstance(result, dict):
        return extract_records(result)
    return []


def fetch_json(url: str, timeout: int) -> Any:
    request = Request(url, headers={"User-Agent": "free-company-intelligence-research/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def atomic_json(path: Path, payload: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=os.getenv("DATA_GOV_IN_API_KEY"))
    parser.add_argument("--resource-id", default=DEFAULT_RESOURCE_ID)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output", type=Path, default=Path("intelligence_pipeline/data/mca_company_master"))
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--start-offset", type=int, default=0)
    parser.add_argument("--max-pages", type=int)
    parser.add_argument("--delay", type=float, default=0.75)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()

    if not args.api_key:
        parser.error("A free data.gov.in key is required via --api-key or DATA_GOV_IN_API_KEY")
    if args.limit < 1:
        parser.error("--limit must be positive")

    output = args.output.resolve()
    raw_dir = output / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output / "checkpoint.json"
    offset = args.start_offset
    if checkpoint_path.exists() and not args.no_resume:
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint.get("resource_id") == args.resource_id:
            offset = int(checkpoint.get("next_offset", offset))

    all_records: list[dict[str, Any]] = []
    existing_jsonl = output / "records.jsonl"
    if existing_jsonl.exists() and not args.no_resume:
        for line in existing_jsonl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                all_records.append(json.loads(line))

    pages = 0
    while args.max_pages is None or pages < args.max_pages:
        query = urlencode({
            "api-key": args.api_key,
            "format": "json",
            "offset": offset,
            "limit": args.limit,
        })
        url = f"{args.base_url.rstrip('/')}/{args.resource_id}?{query}"
        payload = fetch_json(url, args.timeout)
        records = extract_records(payload)
        page_path = raw_dir / f"page_{offset:012d}.json"
        atomic_json(page_path, payload)

        if not records:
            break
        all_records.extend(records)
        offset += len(records)
        pages += 1
        atomic_json(checkpoint_path, {
            "resource_id": args.resource_id,
            "next_offset": offset,
            "pages_completed": pages,
            "records_seen_this_run": len(all_records),
            "updated_at_epoch": time.time(),
        })
        if len(records) < args.limit:
            break
        time.sleep(args.delay)

    output.mkdir(parents=True, exist_ok=True)
    with existing_jsonl.open("w", encoding="utf-8") as handle:
        for record in all_records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

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
    for record in all_records:
        canonical = {field: canonical_value(record, keys) for field, keys in aliases.items()}
        cin = str(canonical.get("cin") or "").strip().upper()
        fallback = hashlib.sha256(json.dumps(record, sort_keys=True, default=str).encode()).hexdigest()
        key = cin or fallback
        canonical["raw_record_json"] = json.dumps(record, ensure_ascii=False, sort_keys=True)
        deduplicated[key] = canonical

    csv_path = output / "companies.csv"
    fieldnames = list(aliases) + ["raw_record_json"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduplicated.values())

    print(json.dumps({
        "raw_pages": pages,
        "records": len(all_records),
        "deduplicated_companies": len(deduplicated),
        "output": str(output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
