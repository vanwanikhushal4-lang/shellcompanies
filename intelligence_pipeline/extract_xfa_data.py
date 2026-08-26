#!/usr/bin/env python3
"""Extract embedded XFA packets and leaf values from supplied MCA forms."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree

from pypdf import PdfReader


def is_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(5) == b"%PDF-"
    except OSError:
        return False


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def flatten_xml(xml: str) -> list[dict[str, str]]:
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        return []
    values: list[dict[str, str]] = []

    def visit(element, path: list[str]) -> None:
        name = local_name(element.tag)
        current = path + [name]
        text = re.sub(r"\s+", " ", element.text or "").strip()
        children = list(element)
        if text and not children:
            values.append({"path": "/".join(current), "field": name, "value": text})
        for key, value in element.attrib.items():
            values.append({"path": "/".join(current), "field": f"@{local_name(key)}", "value": str(value)})
        for child in children:
            visit(child, current)

    visit(root, [])
    return values


def stream_text(value) -> str:
    data = value.get_object().get_data()
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("doc"))
    parser.add_argument("--output", type=Path, default=Path("tmp/pdfs/company_intelligence/xfa"))
    args = parser.parse_args()

    source_root = args.input.resolve()
    output = args.output.resolve()
    packets_dir = output / "packets"
    packets_dir.mkdir(parents=True, exist_ok=True)
    index_path = output / "xfa_values.jsonl"
    docs_with_xfa = 0
    values_written = 0
    errors = 0

    with index_path.open("w", encoding="utf-8") as index:
        for path in sorted(source_root.rglob("*")):
            if not path.is_file() or not is_pdf(path):
                continue
            relative = path.relative_to(source_root)
            try:
                reader = PdfReader(path, strict=False)
                root = reader.trailer["/Root"].get_object()
                acroform_ref = root.get("/AcroForm")
                if not acroform_ref:
                    continue
                acroform = acroform_ref.get_object()
                xfa = acroform.get("/XFA")
                if not xfa:
                    continue
                docs_with_xfa += 1
                document_id = hashlib.sha256(str(relative).encode()).hexdigest()[:20]
                packets: list[tuple[str, str]] = []
                xfa_object = xfa.get_object()
                if isinstance(xfa_object, list):
                    for position in range(0, len(xfa_object) - 1, 2):
                        packet_name = str(xfa_object[position]).lstrip("/")
                        packets.append((packet_name, stream_text(xfa_object[position + 1])))
                else:
                    packets.append(("xfa", stream_text(xfa_object)))

                for packet_name, xml in packets:
                    safe_packet_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", packet_name).strip("_") or "packet"
                    packet_path = packets_dir / f"{document_id}_{safe_packet_name}.xml"
                    packet_path.write_text(xml, encoding="utf-8")
                    if packet_name not in {"datasets", "form", "xfa"}:
                        continue
                    for item in flatten_xml(xml):
                        index.write(json.dumps({
                            "company_folder": relative.parts[0] if relative.parts else "",
                            "relative_path": str(relative),
                            "packet": packet_name,
                            **item,
                        }, ensure_ascii=False) + "\n")
                        values_written += 1
            except Exception as exc:
                errors += 1
                index.write(json.dumps({
                    "relative_path": str(relative),
                    "error": f"{type(exc).__name__}: {exc}",
                }, ensure_ascii=False) + "\n")

    print(json.dumps({
        "documents_with_xfa": docs_with_xfa,
        "values_written": values_written,
        "errors": errors,
        "index": str(index_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
