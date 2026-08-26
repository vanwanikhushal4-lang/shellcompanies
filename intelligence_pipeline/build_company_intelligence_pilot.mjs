import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const ROOT = "/Users/apple/Downloads/Shell companies";
const INPUT = path.join(ROOT, "tmp/pdfs/company_intelligence/company_intelligence_pilot.json");
const OUTPUT_DIR = path.join(ROOT, "outputs/01a03d83-1654-7cd2-aa99-c5741ace2116");
const OUTPUT = path.join(OUTPUT_DIR, "company_intelligence_pilot_5_companies.xlsx");
const PREVIEW_DIR = path.join(ROOT, "tmp/spreadsheet_previews/company_intelligence_pilot");
const data = JSON.parse(await fs.readFile(INPUT, "utf8"));

const wb = Workbook.create();
wb.comments.setSelf({ displayName: "User" });

const COLORS = {
  navy: "#132238",
  blue: "#1F4E78",
  teal: "#0F766E",
  paleBlue: "#EAF2F8",
  paleTeal: "#E7F6F2",
  paleGold: "#FFF6D8",
  paleRed: "#FDECEC",
  paleGray: "#F3F5F7",
  gray: "#5E6B78",
  border: "#CBD5E1",
  white: "#FFFFFF",
  text: "#172033",
};

function colLetter(n) {
  let s = "";
  for (let x = n; x > 0; x = Math.floor((x - 1) / 26)) s = String.fromCharCode(65 + ((x - 1) % 26)) + s;
  return s;
}

function toDateIfNeeded(value, header) {
  if (value == null) return null;
  const dateHeaders = new Set([
    "incorporation_date", "as_of_date", "start_or_event_date", "end_date",
    "effective_date", "modified_at",
  ]);
  if (!dateHeaders.has(header)) return value;
  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}/.test(value)) return new Date(value);
  return value;
}

function objectRows(records, headers) {
  return records.map((r) => headers.map((h) => toDateIfNeeded(r[h], h)));
}

function titleCase(s) {
  return s.replaceAll("_", " ").replace(/\b\w/g, (m) => m.toUpperCase());
}

function setColumnFormat(sheet, header, colIndex, firstDataRow, lastDataRow) {
  if (lastDataRow < firstDataRow) return;
  const col = colLetter(colIndex + 1);
  const range = sheet.getRange(`${col}${firstDataRow}:${col}${lastDataRow}`);
  const lower = header.toLowerCase();
  if (["incorporation_date", "as_of_date", "start_or_event_date", "end_date", "effective_date", "modified_at"].includes(lower)) {
    range.format.numberFormat = "yyyy-mm-dd";
  } else if (lower === "confidence") {
    range.format.numberFormat = "0.00";
  } else if (lower.includes("share_of_turnover")) {
    range.format.numberFormat = "0.00%";
  } else if (lower === "amount_or_holding") {
    range.format.numberFormat = "#,##0.0000";
  } else if (
    lower.includes("_inr") || lower.includes("capital") || lower.includes("turnover") ||
    lower.includes("net_worth") || lower.includes("difference_value") ||
    lower.includes("normalized_value") || lower === "source_value"
  ) {
    range.format.numberFormat = "#,##0.00;[Red](#,##0.00);-";
  } else if (
    lower.includes("count") || lower.includes("documents") || lower.includes("pages") ||
    lower.includes("rows") || lower.includes("values") || lower.includes("file_size")
  ) {
    range.format.numberFormat = "#,##0";
  }
}

function addDataSheet({ name, title, subtitle, records, headers, widths, freezeCols = 2, tableName, wrap = [], dataRowHeight = 28 }) {
  const sheet = wb.worksheets.add(name);
  sheet.showGridLines = false;
  const lastCol = colLetter(headers.length);
  sheet.getRange(`A1:${lastCol}1`).merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A2:${lastCol}2`).merge();
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A1:${lastCol}1`).format = {
    fill: COLORS.navy,
    font: { name: "Aptos Display", size: 18, bold: true, color: COLORS.white },
    verticalAlignment: "center",
  };
  sheet.getRange(`A2:${lastCol}2`).format = {
    fill: COLORS.paleBlue,
    font: { name: "Aptos", size: 10, italic: true, color: COLORS.blue },
    verticalAlignment: "center",
  };
  sheet.getRange(`A1:${lastCol}1`).format.rowHeight = 30;
  sheet.getRange(`A2:${lastCol}2`).format.rowHeight = 26;
  const displayHeaders = headers.map(titleCase);
  sheet.getRange(`A4:${lastCol}4`).values = [displayHeaders];
  sheet.getRange(`A4:${lastCol}4`).format = {
    fill: COLORS.blue,
    font: { name: "Aptos", size: 10, bold: true, color: COLORS.white },
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: COLORS.navy },
  };
  sheet.getRange(`A4:${lastCol}4`).format.rowHeight = 34;

  const rows = objectRows(records, headers);
  if (rows.length) {
    const lastRow = 4 + rows.length;
    sheet.getRange(`A5:${lastCol}${lastRow}`).values = rows;
    sheet.getRange(`A5:${lastCol}${lastRow}`).format = {
      font: { name: "Aptos", size: 9, color: COLORS.text },
      verticalAlignment: "top",
      borders: { insideHorizontal: { style: "thin", color: "#E5EAF0" } },
    };
    sheet.getRange(`A5:${lastCol}${lastRow}`).format.rowHeight = dataRowHeight;
    for (let i = 0; i < headers.length; i++) setColumnFormat(sheet, headers[i], i, 5, lastRow);
    for (const h of wrap) {
      const idx = headers.indexOf(h);
      if (idx >= 0) sheet.getRange(`${colLetter(idx + 1)}5:${colLetter(idx + 1)}${lastRow}`).format.wrapText = true;
    }
    const table = sheet.tables.add(`A4:${lastCol}${lastRow}`, true, tableName);
    table.style = "TableStyleMedium2";
    table.showBandedRows = true;
    table.showFilterButton = true;
  }
  for (let i = 0; i < headers.length; i++) {
    sheet.getRange(`${colLetter(i + 1)}:${colLetter(i + 1)}`).format.columnWidth = widths[i] ?? 18;
  }
  sheet.freezePanes.freezeRows(4);
  if (freezeCols) sheet.freezePanes.freezeColumns(freezeCols);
  return sheet;
}

// Create Summary first for workbook navigation, but populate it after all source sheets exist.
const summary = wb.worksheets.add("Summary");

const profileHeaders = [
  "company_name", "cin", "legal_form", "status", "incorporation_date", "roc",
  "registered_address_latest", "state", "postal_code", "authorised_capital_inr",
  "paid_up_capital_inr", "latest_turnover_inr", "turnover_period", "latest_net_worth_inr",
  "net_worth_period", "regulatory_position", "as_of_date", "profile_source", "profile_locator", "notes",
];
addDataSheet({
  name: "Company Profiles", title: "Five document-backed company profiles",
  subtitle: "Every populated field is traceable to a supplied filing or an official public regulator list; null means not verified.",
  records: data.companies, headers: profileHeaders,
  widths: [36, 24, 34, 14, 15, 16, 62, 18, 12, 20, 20, 22, 15, 22, 18, 58, 15, 62, 46, 54],
  tableName: "CompanyProfilesTable", wrap: ["legal_form", "registered_address_latest", "regulatory_position", "profile_source", "profile_locator", "notes"],
  dataRowHeight: 56,
});

const factHeaders = [
  "fact_id", "company_name", "cin", "field_path", "value_text", "value_numeric", "unit",
  "as_of_or_period", "source", "source_locator", "extraction_method", "confidence",
  "contradiction_group", "notes",
];
addDataSheet({
  name: "Fact Ledger", title: "Field-level evidence ledger",
  subtitle: "204 normalized facts with provenance, locators, extraction method, confidence and explicit contradiction groups.",
  records: data.facts, headers: factHeaders,
  widths: [11, 34, 24, 32, 48, 20, 14, 18, 66, 46, 28, 12, 34, 58],
  tableName: "FactLedgerTable", wrap: ["value_text", "source", "source_locator", "notes"],
  dataRowHeight: 42,
});

const financialHeaders = [
  "company_name", "cin", "period", "statement_scope", "metric", "source_value", "source_unit",
  "normalized_value_inr", "source", "source_locator", "extraction_method", "confidence", "notes",
];
addDataSheet({
  name: "Financials", title: "Normalized financial time series",
  subtitle: "113 source-linked observations. Dow values stated in INR million are normalized to INR in a separate column.",
  records: data.financials, headers: financialHeaders,
  widths: [36, 24, 14, 32, 34, 20, 16, 24, 66, 46, 30, 12, 58],
  tableName: "FinancialsTable", wrap: ["statement_scope", "source", "source_locator", "notes"],
  dataRowHeight: 42,
});

const relationshipHeaders = [
  "company_name", "cin", "relationship_type", "related_party", "related_identifier", "role_or_basis",
  "start_or_event_date", "end_date", "amount_or_holding", "unit", "source", "source_locator",
  "extraction_method", "confidence", "notes",
];
addDataSheet({
  name: "People & Ownership", title: "People, ownership and share events",
  subtitle: "Directors, signatories, subscribers, auditors, holding companies, shareholders and transfers extracted from filings.",
  records: data.relationships, headers: relationshipHeaders,
  widths: [36, 24, 24, 38, 24, 44, 17, 17, 22, 22, 66, 44, 25, 12, 54],
  tableName: "PeopleOwnershipTable", wrap: ["role_or_basis", "source", "source_locator", "notes"],
  dataRowHeight: 44,
});

const addressHeaders = [
  "company_name", "cin", "effective_date", "address", "postal_code", "latitude", "longitude",
  "source", "source_locator", "confidence", "notes",
];
addDataSheet({
  name: "Address History", title: "Registered-office observations",
  subtitle: "Time-aware address records preserve conflicting official observations instead of overwriting them.",
  records: data.addresses, headers: addressHeaders,
  widths: [36, 24, 17, 68, 14, 14, 14, 66, 46, 12, 54],
  tableName: "AddressHistoryTable", wrap: ["address", "source", "source_locator", "notes"],
  dataRowHeight: 52,
});

const activityHeaders = ["company_name", "cin", "period", "activity", "activity_code", "share_of_turnover", "source", "source_locator"];
addDataSheet({
  name: "Activities", title: "Declared principal business activities",
  subtitle: "Activity descriptions and turnover shares are filing facts; they are not inferred classifications.",
  records: data.activities, headers: activityHeaders,
  widths: [36, 24, 14, 48, 18, 20, 66, 46],
  tableName: "ActivitiesTable", wrap: ["activity", "source", "source_locator"],
  dataRowHeight: 40,
});

const regulatoryHeaders = [
  "company_name", "cin", "authority", "list_or_register", "as_of_date", "status_or_classification",
  "row_reference", "source_url", "confidence", "interpretation_limit",
];
addDataSheet({
  name: "Regulatory Intel", title: "Official regulatory observations",
  subtitle: "Dated regulator-list facts are separated from analytical findings and from any shell-company label.",
  records: data.regulatory, headers: regulatoryHeaders,
  widths: [36, 24, 30, 66, 16, 62, 26, 68, 12, 66],
  tableName: "RegulatoryIntelTable", wrap: ["list_or_register", "status_or_classification", "source_url", "interpretation_limit"],
  dataRowHeight: 68,
});

const findingHeaders = [
  "finding_id", "company_name", "cin", "finding_type", "severity", "status", "finding",
  "evidence_a", "locator_a", "evidence_b", "locator_b", "difference_value", "difference_unit", "interpretation_limit",
];
const findingsSheet = addDataSheet({
  name: "Findings", title: "Review findings and source conflicts",
  subtitle: "These are data-quality or consistency observations. None is a shell-company classification or allegation of wrongdoing.",
  records: data.findings, headers: findingHeaders,
  widths: [16, 36, 24, 34, 12, 18, 82, 66, 46, 66, 46, 20, 16, 74],
  tableName: "FindingsTable", wrap: ["finding", "evidence_a", "locator_a", "evidence_b", "locator_b", "interpretation_limit"],
  dataRowHeight: 86,
});
findingsSheet.getRange("E5:E9").conditionalFormats.add("containsText", { text: "high", format: { fill: COLORS.paleRed, font: { bold: true, color: "#9F1239" } } });
findingsSheet.getRange("E5:E9").conditionalFormats.add("containsText", { text: "medium", format: { fill: COLORS.paleGold, font: { bold: true, color: "#854D0E" } } });

const coverageHeaders = [
  "company_name", "cin", "documents", "pdf_pages", "pages_with_embedded_text", "xfa_dataset_values",
  "fact_ledger_rows", "financial_rows", "relationship_rows", "address_observations", "findings",
];
addDataSheet({
  name: "Coverage", title: "Extraction and intelligence coverage",
  subtitle: "Coverage shows what was actually processed and normalized for each of the five supplied company folders.",
  records: data.coverage, headers: coverageHeaders,
  widths: [38, 24, 14, 14, 24, 22, 20, 18, 20, 22, 14],
  tableName: "CoverageTable",
});

const documentHeaders = [
  "document_id", "company_name", "company_folder", "filename", "extension", "file_size_bytes", "modified_at",
  "is_pdf", "page_count", "pages_with_text", "extraction_status", "error", "absolute_path",
];
addDataSheet({
  name: "Documents", title: "Supplied-document manifest",
  subtitle: "206 files indexed with SHA-256 document IDs, page/text coverage and absolute audit paths.",
  records: data.documents, headers: documentHeaders,
  widths: [68, 38, 44, 66, 12, 18, 22, 12, 14, 18, 20, 30, 78],
  tableName: "DocumentsTable", wrap: ["filename", "error", "absolute_path"],
  dataRowHeight: 44,
});

// Summary last so formula references resolve to already-created sheets.
summary.showGridLines = false;
summary.getRange("A1:J2").merge();
summary.getRange("A1").values = [["Company Intelligence Pilot — five companies, real extracted data"]];
summary.getRange("A1:J2").format = {
  fill: COLORS.navy,
  font: { name: "Aptos Display", size: 22, bold: true, color: COLORS.white },
  verticalAlignment: "center",
};
summary.getRange("A3:J3").merge();
summary.getRange("A3").values = [["This replaces the bootstrap/name-list packaging with field-level intelligence extracted from the supplied filings and free official sources."]];
summary.getRange("A3:J3").format = { fill: COLORS.paleBlue, font: { italic: true, color: COLORS.blue, size: 11 }, wrapText: true };
summary.getRange("A3:J3").format.rowHeight = 30;

const cards = [
  ["Companies profiled", "=COUNTA('Company Profiles'!B5:B9)"],
  ["Documents indexed", "=SUM('Coverage'!C5:C9)"],
  ["Evidence facts", "=COUNTA('Fact Ledger'!A5:A208)"],
  ["Financial observations", "=COUNTA('Financials'!A5:A117)"],
  ["People / ownership links", "=COUNTA('People & Ownership'!A5:A40)"],
  ["Review findings", "=COUNTA('Findings'!A5:A9)"],
  ["XFA dataset values", "=SUM('Coverage'!F5:F9)"],
  ["Profile-linked facts", "=SUM('Coverage'!G5:G9)"],
  ["PDF pages", "=SUM('Coverage'!D5:D9)"],
  ["Pages with embedded text", "=SUM('Coverage'!E5:E9)"],
];
for (let i = 0; i < cards.length; i++) {
  const row = i < 5 ? 5 : 8;
  const col = (i % 5) * 2 + 1;
  const c1 = colLetter(col);
  const c2 = colLetter(col + 1);
  summary.getRange(`${c1}${row}:${c2}${row}`).merge();
  summary.getRange(`${c1}${row}`).values = [[cards[i][0]]];
  summary.getRange(`${c1}${row}:${c2}${row}`).format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white, size: 9 }, horizontalAlignment: "center" };
  summary.getRange(`${c1}${row + 1}:${c2}${row + 1}`).merge();
  summary.getRange(`${c1}${row + 1}`).formulas = [[cards[i][1]]];
  summary.getRange(`${c1}${row + 1}:${c2}${row + 1}`).format = { fill: COLORS.paleTeal, font: { bold: true, color: COLORS.teal, size: 18 }, horizontalAlignment: "center", numberFormat: "#,##0" };
}

summary.getRange("A11:J11").merge();
summary.getRange("A11").values = [["Representative new intelligence"]];
summary.getRange("A11:J11").format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 12 } };
summary.getRange("A12:C12").values = [["Company", "Evidence-backed delta", "Treatment"]];
summary.getRange("A12:C12").format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white }, wrapText: true };
summary.getRange("A13:C17").values = [
  ["Balbir Holdings", "RBI-registered Base-layer ICC NBFC; also on FIU-IND's 2026-02-28 FINnet2.0 registration non-compliance list.", "Dated regulatory facts"],
  ["Digivolution", "FY2021 net worth conflicts by INR 446,041 across AOC-4 and MGT-7A; prior-period PBT also conflicts across filings.", "High-priority review"],
  ["Adafoa Technology", "Four MOA versions expose a final main-object rewrite while identical agriculture-heavy ancillary boilerplate remains.", "Document mismatch"],
  ["Baglan FPC", "FY2024/FY2025 financials, capital allotment, auditor term and two registered-office moves with coordinates extracted.", "Structured history"],
  ["Dow Chemical Intl.", "FY2025 turnover/net worth, activities, holding company, shareholders, seven directors and FY2022 consolidated financials extracted.", "Profile + graph edges"],
];
summary.getRange("A13:C17").format = { font: { name: "Aptos", size: 10, color: COLORS.text }, verticalAlignment: "top", wrapText: true, borders: { insideHorizontal: { style: "thin", color: COLORS.border } } };
summary.getRange("A13:A17").format.font = { bold: true, color: COLORS.navy };
summary.getRange("C13:C17").format.fill = COLORS.paleGold;
summary.getRange("A13:C17").format.rowHeight = 42;

summary.getRange("A19:J19").merge();
summary.getRange("A19").values = [["Guardrails and interpretation"]];
summary.getRange("A19:J19").format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 12 } };
summary.getRange("A20:J23").merge(true);
summary.getRange("A20").values = [["• No shell-company labels are assigned. Findings are source conflicts or document-consistency signals requiring review."]];
summary.getRange("A21").values = [["• Only supplied filings and freely accessible official public sources are used; no paid or paywalled data."]];
summary.getRange("A22").values = [["• Missing values remain blank/null; different filing definitions are preserved rather than silently reconciled."]];
summary.getRange("A23").values = [[`• Extraction parsed ${data.metadata.xfa_values_total.toLocaleString("en-US")} XFA packet values from ${data.metadata.documents_with_xfa} documents; ${data.metadata.xfa_dataset_values.toLocaleString("en-US")} were dataset-field values used for company coverage.`]];
summary.getRange("A20:J23").format = { fill: COLORS.paleGray, font: { name: "Aptos", size: 10, color: COLORS.text }, wrapText: true, verticalAlignment: "center" };
summary.getRange("A20:J23").format.rowHeight = 28;
summary.getRange("A1:J23").format.borders = { outside: { style: "thin", color: COLORS.border } };
summary.getRange("A:A").format.columnWidth = 32;
summary.getRange("B:B").format.columnWidth = 78;
summary.getRange("C:C").format.columnWidth = 26;
for (const col of ["D", "E", "F", "G", "H", "I", "J"]) summary.getRange(`${col}:${col}`).format.columnWidth = 15;
summary.freezePanes.freezeRows(3);

await fs.mkdir(PREVIEW_DIR, { recursive: true });
const previews = [
  ["Summary", "A1:J23"], ["Company Profiles", "A1:J12"], ["Fact Ledger", "A1:L18"],
  ["Financials", "A1:M18"], ["People & Ownership", "A1:O18"], ["Address History", "A1:K14"],
  ["Activities", "A1:H12"], ["Regulatory Intel", "A1:J10"], ["Findings", "A1:N12"],
  ["Coverage", "A1:K12"], ["Documents", "A1:M18"],
];
for (const [sheetName, range] of previews) {
  const blob = await wb.render({ sheetName, range, scale: 0.8, format: "png" });
  const safe = sheetName.toLowerCase().replaceAll(/[^a-z0-9]+/g, "_");
  await fs.writeFile(path.join(PREVIEW_DIR, `${safe}.png`), new Uint8Array(await blob.arrayBuffer()));
}

const summaryCheck = await wb.inspect({ kind: "table", range: "Summary!A1:J23", include: "values,formulas", tableMaxRows: 23, tableMaxCols: 10, maxChars: 7000 });
console.log(summaryCheck.ndjson);
const financialCheck = await wb.inspect({ kind: "table", range: "Financials!A4:M12", include: "values,formulas", tableMaxRows: 12, tableMaxCols: 13, maxChars: 4500 });
console.log(financialCheck.ndjson);
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan", maxChars: 4000 });
console.log(errors.ndjson);

await fs.mkdir(OUTPUT_DIR, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(wb);
await output.save(OUTPUT);
console.log(JSON.stringify({ output: OUTPUT, previewDir: PREVIEW_DIR, sheets: previews.length }, null, 2));
