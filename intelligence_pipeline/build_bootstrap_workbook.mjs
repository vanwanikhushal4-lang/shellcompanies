import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "/Users/apple/Downloads/Shell companies";
const tempDir = "/tmp/company-intelligence.XDfAid";
const outputDir = `${root}/outputs/01a03d83-1654-7cd2-aa99-c5741ace2116`;
const input = JSON.parse(await fs.readFile(`${tempDir}/bootstrap_inputs.json`, "utf8"));

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const queue = workbook.worksheets.add("Company Queue");
const sources = workbook.worksheets.add("Free Sources");
const fields = workbook.worksheets.add("Field Priority");
const docPriority = workbook.worksheets.add("Document Priority");
const localDocs = workbook.worksheets.add("Local Documents");
const facts = workbook.worksheets.add("Fact Ledger");
const relationships = workbook.worksheets.add("Relationships");
const legal = workbook.worksheets.add("Legal Events");
const labels = workbook.worksheets.add("Label Evidence");
const conflicts = workbook.worksheets.add("Conflicts");
const runLog = workbook.worksheets.add("Run Log");

const colors = {
  navy: "#17324D",
  blue: "#2C5F8A",
  teal: "#167D7F",
  lightBlue: "#EAF2F8",
  lightTeal: "#E7F4F3",
  amber: "#F5C451",
  lightAmber: "#FFF4D6",
  grey: "#E5E7EB",
  darkGrey: "#4B5563",
  white: "#FFFFFF",
  red: "#B42318",
  green: "#147A50",
};

function columnLetter(index) {
  let value = index + 1;
  let output = "";
  while (value > 0) {
    const remainder = (value - 1) % 26;
    output = String.fromCharCode(65 + remainder) + output;
    value = Math.floor((value - 1) / 26);
  }
  return output;
}

function setHeader(sheet, headers, widths, lastRow = 1) {
  const lastCol = columnLetter(headers.length - 1);
  sheet.getRange(`A1:${lastCol}1`).values = [headers];
  sheet.getRange(`A1:${lastCol}1`).format = {
    fill: colors.navy,
    font: { bold: true, color: colors.white },
    verticalAlignment: "center",
    wrapText: true,
    borders: { bottom: { style: "medium", color: colors.blue } },
  };
  sheet.getRange(`A1:${lastCol}1`).format.rowHeight = 32;
  widths.forEach((width, index) => {
    sheet.getRange(`${columnLetter(index)}1:${columnLetter(index)}${Math.max(1, lastRow)}`).format.columnWidth = width;
  });
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
}

function addTable(sheet, name, rows, cols) {
  const lastCol = columnLetter(cols - 1);
  const table = sheet.tables.add(`A1:${lastCol}${rows}`, true, name);
  table.style = "TableStyleMedium2";
  table.showBandedRows = true;
  table.showFilterButton = true;
}

function createEmptyLedger(sheet, headers, widths) {
  setHeader(sheet, headers, widths, 2);
  sheet.getRange(`A2:${columnLetter(headers.length - 1)}2`).values = [headers.map(() => null)];
  sheet.getRange(`A2:${columnLetter(headers.length - 1)}2`).format.fill = "#F9FAFB";
}

const queueHeaders = [
  "CIN", "Company Name", "Normalized Name", "Pilot Status", "Batch",
  "Research Status", "Identity Status", "Coverage Tier", "Last Updated", "Reviewer", "Notes",
];
const queueRows = input.companies.map((company) => [
  company.cin,
  company.company_name,
  company.normalized_name,
  null,
  null,
  "Not Started",
  "Seeded from supplied workbook",
  "Unreviewed",
  null,
  null,
  null,
]);
queue.getRangeByIndexes(1, 0, queueRows.length, queueHeaders.length).values = queueRows;
setHeader(queue, queueHeaders, [24, 38, 38, 14, 10, 17, 27, 15, 15, 18, 36], queueRows.length + 1);
queue.getRange("D2").formulas = [["=IF(ROW()<=26,\"PILOT\",\"BACKLOG\")"]];
queue.getRange(`D2:D${queueRows.length + 1}`).fillDown();
queue.getRange("E2").formulas = [["=INT((ROW()-2)/25)+1"]];
queue.getRange(`E2:E${queueRows.length + 1}`).fillDown();
queue.getRange(`I2:I${queueRows.length + 1}`).format.numberFormat = "yyyy-mm-dd hh:mm";
queue.getRange(`F2:F${queueRows.length + 1}`).dataValidation = {
  rule: { type: "list", values: ["Not Started", "In Progress", "Needs Review", "Complete", "Blocked"] },
};
queue.getRange(`H2:H${queueRows.length + 1}`).dataValidation = {
  rule: { type: "list", values: ["Unreviewed", "Bronze", "Silver", "Gold"] },
};
queue.getRange(`F2:F${queueRows.length + 1}`).conditionalFormats.add("containsText", {
  text: "Complete",
  format: { fill: "#DCFCE7", font: { color: colors.green, bold: true } },
});
queue.getRange(`F2:F${queueRows.length + 1}`).conditionalFormats.add("containsText", {
  text: "Blocked",
  format: { fill: "#FEE2E2", font: { color: colors.red, bold: true } },
});
queue.getRange(`D2:D${queueRows.length + 1}`).conditionalFormats.add("containsText", {
  text: "PILOT",
  format: { fill: colors.lightAmber, font: { color: "#7A4E00", bold: true } },
});
addTable(queue, "CompanyQueueTable", queueRows.length + 1, queueHeaders.length);

const sourceHeaders = [
  "Source ID", "Source Name", "Publisher", "Base URL", "Access Mode",
  "Automation Level", "Primary Uses", "Free-only Notes",
];
const sourceRows = input.sources.map((row) => [
  row.source_id, row.source_name, row.publisher, row.base_url, row.access_mode,
  row.automation_level, row.primary_uses, row.free_only_notes,
]);
sources.getRangeByIndexes(1, 0, sourceRows.length, sourceHeaders.length).values = sourceRows;
setHeader(sources, sourceHeaders, [13, 30, 34, 48, 21, 22, 45, 52], sourceRows.length + 1);
sources.getRange(`A2:H${sourceRows.length + 1}`).format.wrapText = true;
addTable(sources, "FreeSourcesTable", sourceRows.length + 1, sourceHeaders.length);

const fieldHeaders = ["Field Name", "Rules Unlocked", "Categories Served", "Source Documents", "Example Rule IDs"];
const fieldRows = input.fields.map((row) => [
  row.field_name, row.rules_unlocked, row.categories_served, row.source_documents, row.example_rule_ids,
]);
fields.getRangeByIndexes(1, 0, fieldRows.length, fieldHeaders.length).values = fieldRows;
setHeader(fields, fieldHeaders, [34, 16, 55, 62, 32], fieldRows.length + 1);
fields.getRange(`B2:B${fieldRows.length + 1}`).format.numberFormat = "#,##0";
addTable(fields, "FieldPriorityTable", fieldRows.length + 1, fieldHeaders.length);

const docHeaders = [
  "Source Document", "Group", "Primary Rules", "Fallback Uses", "Critical", "High", "Medium", "Low", "Categories Served",
];
const docRows = input.document_priorities.map((row) => [
  row.source_document, row.group, row.primary_rules_unlocked, row.fallback_uses,
  row.critical, row.high, row.medium, row.low, row.categories_served,
]);
docPriority.getRangeByIndexes(1, 0, docRows.length, docHeaders.length).values = docRows;
setHeader(docPriority, docHeaders, [46, 22, 15, 15, 11, 11, 11, 11, 60], docRows.length + 1);
docPriority.getRange(`C2:H${docRows.length + 1}`).format.numberFormat = "#,##0";
addTable(docPriority, "DocumentPriorityTable", docRows.length + 1, docHeaders.length);

const localHeaders = ["Company Folder", "Filename", "Extension", "File Size Bytes", "SHA-256", "Local Path", "Modified At"];
const localRows = input.local_documents.map((row) => [
  row.company_folder, row.filename, row.extension, row.file_size_bytes, row.sha256, row.local_path, new Date(row.modified_at),
]);
localDocs.getRangeByIndexes(1, 0, localRows.length, localHeaders.length).values = localRows;
setHeader(localDocs, localHeaders, [40, 58, 12, 17, 68, 90, 22], localRows.length + 1);
localDocs.getRange(`D2:D${localRows.length + 1}`).format.numberFormat = "#,##0";
localDocs.getRange(`G2:G${localRows.length + 1}`).format.numberFormat = "yyyy-mm-dd hh:mm";
addTable(localDocs, "LocalDocumentsTable", localRows.length + 1, localHeaders.length);

createEmptyLedger(facts, [
  "Fact ID", "Company ID", "CIN", "Field Name", "Value", "Value Type", "Unit", "Currency",
  "Period Start", "Period End", "As-of Date", "Source Publisher", "Source Type", "Document ID",
  "Document Title", "Document Date", "Source URL", "Page or Locator", "Retrieved At",
  "Extraction Method", "Confidence", "Reviewer Status", "Notes",
], [18, 18, 24, 30, 35, 14, 13, 11, 14, 14, 14, 28, 20, 18, 46, 14, 50, 18, 20, 20, 13, 18, 38]);

createEmptyLedger(relationships, [
  "Relationship ID", "Source Entity Type", "Source Entity ID", "Source Entity Name", "Edge Type",
  "Target Entity Type", "Target Entity ID", "Target Entity Name", "Start Date", "End Date",
  "Document ID", "Source URL", "Page or Locator", "Confidence", "Reviewer Status",
], [20, 20, 24, 36, 24, 20, 24, 36, 14, 14, 18, 50, 18, 13, 18]);

createEmptyLedger(legal, [
  "Event ID", "Company ID", "CIN", "Agency or Court", "Action Type", "Case Reference", "Company Role",
  "Event Date", "Allegation", "Finding", "Amount", "Currency", "Procedural Status", "Outcome",
  "Document ID", "Source URL", "Page or Locator", "Reviewer Status",
], [18, 18, 24, 28, 24, 26, 18, 14, 44, 44, 16, 11, 22, 36, 18, 50, 18, 18]);

createEmptyLedger(labels, [
  "Label Evidence ID", "Company ID", "CIN", "Label", "Label Status", "Confidence", "Reason", "Authority",
  "Document ID", "Document Date", "Source URL", "Page or Locator", "Independently Verified",
  "Exclude From Features", "Reviewer Status",
], [22, 18, 24, 28, 20, 13, 50, 30, 18, 14, 50, 18, 22, 22, 18]);

createEmptyLedger(conflicts, [
  "Conflict ID", "Company ID", "CIN", "Field Name", "Value A", "Source A", "Value B", "Source B",
  "Conflict Status", "Resolution", "Reviewer", "Reviewed At",
], [18, 18, 24, 28, 32, 40, 32, 40, 18, 42, 18, 20]);

summary.showGridLines = false;
summary.mergeCells("A1:F1");
summary.getRange("A1:F1").values = [["Company Intelligence Dataset — Free-Source Bootstrap"]];
summary.getRange("A1:F1").format = {
  fill: colors.navy,
  font: { bold: true, color: colors.white, size: 18 },
  horizontalAlignment: "left",
  verticalAlignment: "center",
};
summary.getRange("A1:F1").format.rowHeight = 42;
summary.getRange("A3:C3").values = [["Metric", "Value", "Interpretation"]];
summary.getRange("A3:C3").format = { fill: colors.blue, font: { bold: true, color: colors.white } };
summary.getRange("A4:A9").values = [["Companies in queue"], ["Pilot companies"], ["Priority fields"], ["Document types"], ["Local evidence files"], ["Free source entries"]];
summary.getRange("B4:B9").formulas = [
  [`=COUNTA('Company Queue'!$A$2:$A$${queueRows.length + 1})`],
  [`=COUNTIF('Company Queue'!$D$2:$D$${queueRows.length + 1},\"PILOT\")`],
  [`=COUNTA('Field Priority'!$A$2:$A$${fieldRows.length + 1})`],
  [`=COUNTA('Document Priority'!$A$2:$A$${docRows.length + 1})`],
  [`=COUNTA('Local Documents'!$A$2:$A$${localRows.length + 1})`],
  [`=COUNTA('Free Sources'!$A$2:$A$${sourceRows.length + 1})`],
];
summary.getRange("C4:C9").values = [
  ["CIN-based starting universe from the supplied workbook"],
  ["First batch marked for end-to-end verification"],
  ["Ordered by how many detection rules each field unlocks"],
  ["Ordered by detection coverage in the supplied indicator library"],
  ["Existing files hashed and indexed; .DS_Store files excluded"],
  ["Official and issuer-published sources; no paid providers"],
];
summary.getRange("A4:C9").format.borders = { preset: "inside", style: "thin", color: colors.grey };
summary.getRange("B4:B9").format = { fill: colors.lightTeal, font: { bold: true, color: colors.teal }, numberFormat: "#,##0" };
summary.getRange("A11:F11").merge();
summary.getRange("A11:F11").values = [["Collection rule: free public data only. Missing values remain null. No CAPTCHA bypass, paid MCA documents, leaked data, or guessed labels."]];
summary.getRange("A11:F11").format = { fill: colors.lightAmber, font: { bold: true, color: "#7A4E00" }, wrapText: true };
summary.getRange("A11:F11").format.rowHeight = 38;
summary.getRange("A13:F13").merge();
summary.getRange("A13:F13").values = [["Workflow: research the 25 PILOT rows → record every fact in Fact Ledger → connect entities in Relationships → isolate official labels in Label Evidence → log contradictions in Conflicts → independent review."]];
summary.getRange("A13:F13").format = { fill: colors.lightBlue, font: { color: colors.navy }, wrapText: true };
summary.getRange("A13:F13").format.rowHeight = 44;
summary.getRange("A1:F15").format.font.name = "Aptos";
summary.getRange("A:A").format.columnWidth = 26;
summary.getRange("B:B").format.columnWidth = 16;
summary.getRange("C:C").format.columnWidth = 66;
summary.getRange("D:F").format.columnWidth = 14;
summary.freezePanes.freezeRows(3);

setHeader(runLog, ["Timestamp", "Stage", "Status", "Records", "Details"], [23, 30, 15, 14, 75], 6);
const generatedAt = new Date(input.generated_at);
runLog.getRange("A2:E6").values = [
  [generatedAt, "Input inventory", "Complete", input.companies.length, "Unique CIN/company rows loaded from Com_name&CIN.xlsx"],
  [generatedAt, "Indicator inventory", "Complete", input.fields.length, "Field Dictionary rows loaded"],
  [generatedAt, "Document priority", "Complete", input.document_priorities.length, "Document Catalogue rows loaded"],
  [generatedAt, "Local evidence manifest", "Complete", input.local_documents.length, "Files hashed with SHA-256; .DS_Store excluded"],
  [generatedAt, "MCA API extraction", "Waiting for free key", 0, "Collector and Postman collection created; DATA_GOV_IN_API_KEY is not present"],
];
runLog.getRange("A2:A6").format.numberFormat = "yyyy-mm-dd hh:mm";
addTable(runLog, "RunLogTable", 6, 5);

await fs.mkdir(outputDir, { recursive: true });

const inspections = [];
inspections.push((await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 5000 })).ndjson);
inspections.push((await workbook.inspect({
  kind: "table",
  sheetId: "Company Queue",
  range: "A1:K8",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 11,
  maxChars: 6000,
})).ndjson);
inspections.push((await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
  maxChars: 5000,
})).ndjson);
await fs.writeFile(`${tempDir}/bootstrap_inspection.ndjson`, inspections.join("\n"), "utf8");

const previewRanges = {
  "Summary": "A1:F15",
  "Company Queue": "A1:K12",
  "Free Sources": "A1:H12",
  "Field Priority": "A1:E12",
  "Document Priority": "A1:I12",
  "Local Documents": "A1:G12",
  "Fact Ledger": "A1:W2",
  "Relationships": "A1:O2",
  "Legal Events": "A1:R2",
  "Label Evidence": "A1:O2",
  "Conflicts": "A1:L2",
  "Run Log": "A1:E6",
};
for (const [sheetName, range] of Object.entries(previewRanges)) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  const safe = sheetName.toLowerCase().replaceAll(" ", "_");
  await fs.writeFile(`${tempDir}/preview_${safe}.png`, new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
const outputPath = `${outputDir}/company_intelligence_bootstrap.xlsx`;
await output.save(outputPath);
console.log(JSON.stringify({
  outputPath,
  companies: queueRows.length,
  fields: fieldRows.length,
  documentTypes: docRows.length,
  localDocuments: localRows.length,
  freeSources: sourceRows.length,
  sheets: Object.keys(previewRanges).length,
}, null, 2));
