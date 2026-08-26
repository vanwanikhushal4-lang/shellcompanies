# Free Company Intelligence Pipeline

This project turns the supplied company queue and document library into a provenance-first research dataset. It uses only lawfully accessible, free public sources.

## Non-negotiable collection rules

- No paid databases, paid APIs, paid MCA downloads, trials requiring payment details, leaked data, credential sharing, CAPTCHA bypassing, or access-control circumvention.
- Respect each source's terms, robots controls, rate limits, and technical access restrictions.
- Missing information remains `null`; never infer a fact merely to complete a row.
- Keep allegations, investigations, interim orders, final findings, convictions, strike-off, dormancy, and restoration as separate states.
- Network patterns are detection features. They are not ground-truth shell-company labels.
- Every material value must retain publisher, document title/date, URL, page or locator, retrieval time, and confidence.

## Supplied inventory

- `Com_name&CIN.xlsx`: 41,452 company records.
- `Shell_Company_Indicator_Library_3.xlsx`: 407 indicators, 2,199 fields, and 90 document types.
- `doc/`: existing company documents. The generated bootstrap workbook contains a hashed manifest.

## MCA/data.gov.in extraction

1. Obtain a free API key from data.gov.in.
2. Set it without committing it to disk:

   ```bash
   export DATA_GOV_IN_API_KEY='your-free-key'
   ```

3. Run:

   ```bash
   python3 intelligence_pipeline/mca_company_master.py --output intelligence_pipeline/data/mca_company_master
   ```

The collector stores every raw API page, resumes from a checkpoint, preserves each original record as JSON, and writes a deduplicated canonical CSV. The catalog resource is a seed and may have a historical coverage date; it is not treated as the only source of truth.

The Postman collection in `postman/` is useful for validating and paging through the endpoint. Use the Python collector for durable bulk extraction because Postman Runner is not a reliable data store.

## Dataset layers

- Company queue: identity and research workflow.
- Fact ledger: field-level, time-aware values with provenance.
- Document manifest: raw evidence inventory with hashes.
- Relationships: graph-ready company/person/address/auditor/shareholder edges.
- Legal events: allegations and adjudicated outcomes kept separate.
- Label evidence: official ground truth only, isolated from model features.
- Conflicts: contradictory source values retained for review.

Begin with the first 25 companies, verify citations manually, and only then increase batch size.
