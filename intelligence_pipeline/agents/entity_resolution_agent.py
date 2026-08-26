"""Subagent 5: Entity Resolution Agent

Resolves company aliases, CINs, DINs, GSTINs, addresses, and key personnel
into unified canonical entity records without merging uncertain identities.
"""

from __future__ import annotations

import re
from typing import Any


class EntityResolutionAgent:
    def __init__(self) -> None:
        self.alias_table: dict[str, set[str]] = {}

    def normalize_name(self, name: str) -> str:
        if not name:
            return ""
        clean = re.sub(r"\b(private|limited|pvt|ltd|company|co|inc|corp)\b", "", name, flags=re.IGNORECASE)
        clean = re.sub(r"[^\w\s]", "", clean)
        return " ".join(clean.upper().split())

    def register_alias(self, canonical_cin: str, name: str) -> None:
        norm = self.normalize_name(name)
        if norm:
            if canonical_cin not in self.alias_table:
                self.alias_table[canonical_cin] = set()
            self.alias_table[canonical_cin].add(norm)

    def validate_cin(self, cin: str) -> bool:
        if not cin or not isinstance(cin, str):
            return False
        cin_clean = cin.strip().upper()
        pattern = r"^[UL]\d{5}[A-Z]{2}\d{4}(PLC|PTC|SGC|FLC|ULL|NPL)\d{6}$"
        return bool(re.match(pattern, cin_clean))

    def validate_din(self, din: str) -> bool:
        if not din:
            return False
        return bool(re.match(r"^\d{8}$", str(din).strip()))

    def validate_gstin(self, gstin: str) -> bool:
        if not gstin:
            return False
        pattern = r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        return bool(re.match(pattern, str(gstin).strip().upper()))


if __name__ == "__main__":
    print("EntityResolutionAgent initialized successfully.")
