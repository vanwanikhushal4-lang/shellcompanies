"""Repair script to convert all synthetic text PDF files into valid binary PDFs

and synchronize updated SHA-256 file hashes in document_manifest.csv files.
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from intelligence_pipeline.utils.pdf_generator import convert_text_to_pdf
from intelligence_pipeline.schemas.deliverable_headers import DOCUMENT_MANIFEST_HEADERS
from intelligence_pipeline.export_deliverables import write_csv


def is_fake_pdf(filepath: Path) -> tuple[bool, str]:
    try:
        with filepath.open("rb") as f:
            data = f.read()
        if not data.startswith(b"%PDF-"):
            return True, "Does not start with %PDF-"
        if b"xref" not in data and b"obj" not in data and b"startxref" not in data:
            try:
                text_content = data.decode("utf-8")
                return True, text_content
            except UnicodeDecodeError:
                return True, "Invalid binary PDF structure"
        return False, ""
    except Exception as e:
        return True, str(e)


def repair_directory_pdfs(target_dir: Path) -> dict[str, str]:
    """Scans and converts fake PDFs in target_dir. Returns dict of rel_filename -> new_hash."""
    updated_hashes: dict[str, str] = {}
    converted_count = 0
    skipped_count = 0

    print(f"Scanning directory: {target_dir}")
    for root, _, files in os.walk(target_dir):
        for f in files:
            if not f.lower().endswith(".pdf"):
                continue

            filepath = Path(root) / f
            fake, content_or_reason = is_fake_pdf(filepath)

            if fake:
                if isinstance(content_or_reason, str) and content_or_reason.startswith("Does not start with") or content_or_reason == "Invalid binary PDF structure":
                    # Read text with errors='replace'
                    content = filepath.read_text(encoding="utf-8", errors="replace")
                else:
                    content = content_or_reason

                # Convert to valid PDF
                convert_text_to_pdf(content, filepath)

                # Recompute SHA-256 hash
                hasher = hashlib.sha256()
                hasher.update(filepath.read_bytes())
                new_hash = hasher.hexdigest()

                # Calculate relative filename matching document_manifest.csv
                # e.g., documents/<Company_Folder>/<filename>.pdf
                rel_parts = filepath.relative_to(target_dir.parent).parts
                rel_filename = "/".join(rel_parts)

                updated_hashes[rel_filename] = new_hash
                converted_count += 1
            else:
                skipped_count += 1

    print(f"  Done scanning {target_dir.name}: Converted {converted_count} files, {skipped_count} already valid.")
    return updated_hashes


def update_manifest(manifest_path: Path, updated_hashes: dict[str, str]) -> None:
    if not manifest_path.exists():
        print(f"Manifest path not found: {manifest_path}")
        return

    with manifest_path.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    updated_count = 0
    for row in rows:
        fn = row.get("local_filename", "")
        # Normalize slashes
        fn_norm = fn.replace("\\", "/")
        if fn_norm in updated_hashes:
            row["file_hash"] = updated_hashes[fn_norm]
            updated_count += 1

    write_csv(manifest_path, DOCUMENT_MANIFEST_HEADERS, rows)
    print(f"Updated {updated_count} hashes in {manifest_path.name}")


def main() -> None:
    pilot_25_dir = ROOT_DIR / "outputs" / "pilot_25" / "documents"
    batch_50_dir = ROOT_DIR / "outputs" / "batch_50" / "documents"
    combined_75_dir = ROOT_DIR / "outputs" / "combined_75" / "documents"

    pilot_hashes = repair_directory_pdfs(pilot_25_dir)
    update_manifest(ROOT_DIR / "outputs" / "pilot_25" / "document_manifest.csv", pilot_hashes)

    batch_hashes = repair_directory_pdfs(batch_50_dir)
    update_manifest(ROOT_DIR / "outputs" / "batch_50" / "document_manifest.csv", batch_hashes)

    if combined_75_dir.exists():
        from intelligence_pipeline.merge_deliverables import main as merge_main
        print("\nRe-merging deliverables into outputs/combined_75...")
        merge_main()

    print("\nPDF Repair and Manifest Hash Synchronization Complete!")


if __name__ == "__main__":
    main()
