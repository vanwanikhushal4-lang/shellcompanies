#!/usr/bin/env python3
"""Extract page-level text from the supplied evidence library for analysis."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(5) == b"%PDF-"
    except OSError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("doc"))
    parser.add_argument("--output", type=Path, default=Path("tmp/pdfs/company_intelligence"))
    args = parser.parse_args()

    source_root = args.input.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "document_manifest.jsonl"
    pages_path = output / "page_text.jsonl"

    documents = 0
    pdfs = 0
    pages = 0
    pages_with_text = 0
    errors = 0

    with manifest_path.open("w", encoding="utf-8") as manifest, pages_path.open("w", encoding="utf-8") as page_file:
        for path in sorted(source_root.rglob("*")):
            if not path.is_file() or path.name == ".DS_Store":
                continue
            documents += 1
            relative = path.relative_to(source_root)
            company_folder = relative.parts[0] if relative.parts else ""
            record = {
                "document_id": sha256(path),
                "company_folder": company_folder,
                "relative_path": str(relative),
                "absolute_path": str(path),
                "filename": path.name,
                "extension": path.suffix.lower(),
                "file_size_bytes": path.stat().st_size,
                "modified_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
                "is_pdf": is_pdf(path),
                "page_count": None,
                "pages_with_text": 0,
                "extraction_status": "not_pdf",
                "error": None,
            }
            if record["is_pdf"]:
                pdfs += 1
                try:
                    reader = PdfReader(path, strict=False)
                    if reader.is_encrypted:
                        reader.decrypt("")
                    record["page_count"] = len(reader.pages)
                    record["extraction_status"] = "complete"
                    for page_index, page in enumerate(reader.pages, start=1):
                        pages += 1
                        try:
                            text = page.extract_text(extraction_mode="layout") or ""
                        except Exception:
                            text = page.extract_text() or ""
                        text = text.replace("\x00", "").strip()
                        if text:
                            pages_with_text += 1
                            record["pages_with_text"] += 1
                        page_file.write(json.dumps({
                            "document_id": record["document_id"],
                            "company_folder": company_folder,
                            "relative_path": str(relative),
                            "page": page_index,
                            "text": text,
                        }, ensure_ascii=False) + "\n")
                except Exception as exc:
                    errors += 1
                    record["extraction_status"] = "error"
                    record["error"] = f"{type(exc).__name__}: {exc}"
            manifest.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(json.dumps({
        "documents": documents,
        "pdfs": pdfs,
        "pages": pages,
        "pages_with_text": pages_with_text,
        "errors": errors,
        "manifest": str(manifest_path),
        "page_text": str(pages_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
