#!/usr/bin/env python3
"""Reduce a card or expense export to a count of distinct AI vendors.

Input: a CSV or JSON export from a card or expense platform. The reducer reads,
per line:

  merchant    Merchant, Merchant name, Vendor, Payee, Description or
              Statement descriptor (used only for the AI-vendor match; never
              printed)
  personal    Reimbursable, Payment method, Card type or Funding source; a
              value of true, yes, personal, out of pocket or reimbursement
              marks the line as personal spend reimbursed by the company

Amounts, dates and employee names are never read. The column names and the
personal-spend markers are the maintainer's assumption about common export
shapes (Tier D), and card descriptors are often truncated, so the vendor count
is a floor.

Output: ai-vendors-in-spend, ai-spend-lines and ai-spend-lines-personal-card.
No signal key: spend shows that AI is bought, not which surface it runs on.

Usage: python scripts/reducers/expense_ai_vendors.py EXPORT.csv|EXPORT.json
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, field, read_rows  # noqa: E402
from ai_catalog import ai_vendor  # noqa: E402

OBS = {"ai-vendors-in-spend", "ai-spend-lines", "ai-spend-lines-personal-card"}
PERSONAL = ("true", "yes", "personal", "out of pocket", "out-of-pocket", "reimburs")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        sys.exit(__doc__.strip().splitlines()[-1])
    vendors, lines, personal = set(), 0, 0
    for row in read_rows(argv[0]):
        vendor = ai_vendor(field(row, "Merchant", "Merchant name", "Vendor", "Payee"),
                           field(row, "Description", "Statement descriptor"))
        if not vendor:
            continue
        vendors.add(vendor)
        lines += 1
        flag = str(field(row, "Reimbursable", "Payment method", "Card type", "Funding source") or "").lower()
        if any(p in flag for p in PERSONAL):
            personal += 1
    emit("expense-ai-vendors", 1,
         {"ai-vendors-in-spend": len(vendors), "ai-spend-lines": lines, "ai-spend-lines-personal-card": personal},
         {}, OBS, set())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
