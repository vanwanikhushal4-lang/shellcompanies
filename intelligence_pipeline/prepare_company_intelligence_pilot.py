#!/usr/bin/env python3
"""Prepare a curated, source-linked pilot dataset from the supplied company filings.

The output is an intermediate JSON file consumed by the workbook builder.  It contains
only facts verified from the supplied public filings or named official regulator lists.
It does not assign a shell-company label.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path("/Users/apple/Downloads/Shell companies")
TMP = ROOT / "tmp/pdfs/company_intelligence"
OUT = TMP / "company_intelligence_pilot.json"


def ap(rel: str) -> str:
    return str((ROOT / rel).resolve())


SRC = {
    "ada_master": ap("doc/Adafoa technology Pvt ltd/Master data  MCA Services.pdf"),
    "ada_coi": ap("doc/Adafoa technology Pvt ltd/CERTIFICATE OF INCORPORATION-20220110_1769402802957.pdf"),
    "ada_moa_14": ap("doc/Adafoa technology Pvt ltd/Form SPICe MOA (INC-33)-14122021_1769402886001.pdf"),
    "ada_moa_16": ap("doc/Adafoa technology Pvt ltd/Form SPICe MOA (INC-33)-16122021_1769402883840.pdf"),
    "ada_moa_29": ap("doc/Adafoa technology Pvt ltd/Form SPICe MOA (INC-33)-29122021_1769402888643.pdf"),
    "ada_moa_06": ap("doc/Adafoa technology Pvt ltd/Form SPICe MOA (INC-33)-06012022_1769402887509.pdf"),
    "bal_master": ap("doc/BALBIR HOLDINGS PRIVATE LIMITED/Master datars - MCA Services.pdf"),
    "bal_aoc18": ap("doc/BALBIR HOLDINGS PRIVATE LIMITED/Form AOC-4-18122018_signed_1769401335724.pdf"),
    "bal_aoc19": ap("doc/BALBIR HOLDINGS PRIVATE LIMITED/Form AOC-4-07122019_signed_1769401344896.pdf"),
    "bal_mgt20": ap("doc/BALBIR HOLDINGS PRIVATE LIMITED/Form MGT-7-02032021_signed_1769401226041.pdf"),
    "dig_master": ap("doc/Digivolution consultancy Pvt lt/Master data - MCA Services.pdf"),
    "dig_inc20a": ap("doc/Digivolution consultancy Pvt lt/INC-20A_Form INC20A_12_06_2019.pdf"),
    "dig_inc22": ap("doc/Digivolution consultancy Pvt lt/INC-22_Form INC22_21_08_2019.pdf"),
    "dig_mgt14": ap("doc/Digivolution consultancy Pvt lt/MGT-14_Certificate of registration of the Special Resolution confirming alteration of object clauses_28_04_2020.pdf"),
    "dig_fs20": ap("doc/Digivolution consultancy Pvt lt/AOC-4_Copy of Financial Staements duly authenticated as per section 134 Including Boards report auditors ..._22_01_2021.pdf"),
    "dig_aoc20": ap("doc/Digivolution consultancy Pvt lt/AOC-4_Form AOC4_22_01_2021.pdf"),
    "dig_aoc21": ap("doc/Digivolution consultancy Pvt lt/AOC-4_Form AOC4_31_01_2022.pdf"),
    "dig_mgt21": ap("doc/Digivolution consultancy Pvt lt/MGT-7A_Form MGT7A_31_01_2022.pdf"),
    "bag_coi": ap("doc/BAGLAN FARMERS PRODUCER COMPANY LIMITED-20260803T053634Z-1-001/BAGLAN FARMERS PRODUCER COMPANY LIMITED/Certificate/SPICE + Part B_Certificate of Incorporation_25_01_2019.pdf"),
    "bag_aoc25": ap("doc/BAGLAN FARMERS PRODUCER COMPANY LIMITED-20260803T053634Z-1-001/BAGLAN FARMERS PRODUCER COMPANY LIMITED/Annual Filing/U01100MH2019PTC320804_UU3480759 (1)/AOC-4_Form AOC4_18_11_2025.pdf"),
    "bag_inc22_19": ap("doc/BAGLAN FARMERS PRODUCER COMPANY LIMITED-20260803T053634Z-1-001/BAGLAN FARMERS PRODUCER COMPANY LIMITED/Other eForm Documents/INC-22_Form INC22_08_03_2019.pdf"),
    "bag_inc22_23": ap("doc/BAGLAN FARMERS PRODUCER COMPANY LIMITED-20260803T053634Z-1-001/BAGLAN FARMERS PRODUCER COMPANY LIMITED/Other eForm Documents/INC-22_Form INC22_29_04_2023.pdf"),
    "bag_inc22_25": ap("doc/BAGLAN FARMERS PRODUCER COMPANY LIMITED-20260803T053634Z-1-001/BAGLAN FARMERS PRODUCER COMPANY LIMITED/Other eForm Documents/INC-22_Form INC22_17_11_2025.pdf"),
    "bag_pas3": ap("doc/BAGLAN FARMERS PRODUCER COMPANY LIMITED-20260803T053634Z-1-001/BAGLAN FARMERS PRODUCER COMPANY LIMITED/Other eForm Documents/PAS-3_Form PAS3_03_04_2024.pdf"),
    "bag_adt25": ap("doc/BAGLAN FARMERS PRODUCER COMPANY LIMITED-20260803T053634Z-1-001/BAGLAN FARMERS PRODUCER COMPANY LIMITED/Other eForm Documents/ADT - 1_Form ADT1_14_10_2025.pdf"),
    "dow_mgt25": ap("doc/DOW CHEMICAL INTERNATIONAL PRIVATE LIMITED/Annual Filing/MGT-7_Form MGT7_08_10_2025.pdf"),
    "dow_sh23": ap("doc/DOW CHEMICAL INTERNATIONAL PRIVATE LIMITED/Annual Filing/MGT-7_List of share holders debenture holders_23_11_2023.pdf"),
    "dow_fs22": ap("doc/DOW CHEMICAL INTERNATIONAL PRIVATE LIMITED/Annual Filing/AOC-4 XBRL_XBRL document in respect Consolidated financial statement_22_11_2022.pdf"),
    "dow_aoc25": ap("doc/DOW CHEMICAL INTERNATIONAL PRIVATE LIMITED/Annual Filing/AOC-4 XBRL_Form AOC4XBRL_10_10_2025.pdf"),
}

RBI_URL = "https://www.rbi.org.in/hindi1/Upload/content/PDFs/NBFCsandARCs26032024.PDF"
FIU_URL = "https://fiuindia.gov.in/pdfs/downloads/NonCompliantNBFC28022026.pdf"


companies = [
    {
        "company_name": "ADAFOA TECHNOLOGY PRIVATE LIMITED",
        "cin": "U72200DL2022PTC392185",
        "legal_form": "Private company limited by shares; non-government; small company",
        "status": "Active",
        "incorporation_date": "2022-01-07",
        "roc": "ROC Delhi",
        "registered_address_latest": "House No. 353, Block CB, Naraina Village, South West Delhi, Delhi 110028",
        "state": "Delhi",
        "postal_code": "110028",
        "authorised_capital_inr": 100000,
        "paid_up_capital_inr": 100000,
        "latest_turnover_inr": None,
        "turnover_period": None,
        "latest_net_worth_inr": None,
        "net_worth_period": None,
        "regulatory_position": None,
        "as_of_date": "2026-01-26",
        "profile_source": SRC["ada_master"],
        "profile_locator": "MCA master-data snapshot, pages 1-2",
        "notes": "Four XFA MOA versions were extracted; object-clause inconsistency is listed in Findings.",
    },
    {
        "company_name": "BALBIR HOLDINGS PRIVATE LIMITED",
        "cin": "U65990MH1996PTC101262",
        "legal_form": "Private company limited by shares; non-government",
        "status": "Active",
        "incorporation_date": "1996-07-18",
        "roc": "ROC Mumbai",
        "registered_address_latest": "Hotel Pritam Building, Central Avenue, Nagpur, Maharashtra 440002",
        "state": "Maharashtra",
        "postal_code": "440002",
        "authorised_capital_inr": 20000000,
        "paid_up_capital_inr": 20000000,
        "latest_turnover_inr": 3513766.11,
        "turnover_period": "FY2020",
        "latest_net_worth_inr": 22247252.06,
        "net_worth_period": "FY2020",
        "regulatory_position": "RBI-registered Base-layer ICC NBFC; no public-deposit CoR. FIU-IND FINnet2.0 registration non-compliance list as of 2026-02-28.",
        "as_of_date": "2026-02-28",
        "profile_source": RBI_URL,
        "profile_locator": "RBI row 1537, PDF page 29; FIU-IND row 3566, PDF page 94",
        "notes": "The MCA master snapshot shows postcode 000000; RBI and FIU-IND both show 440002.",
    },
    {
        "company_name": "DIGIVOLUTION CONSULTANCY PRIVATE LIMITED",
        "cin": "U74999MH2019PTC324789",
        "legal_form": "Private company limited by shares; non-government; small company",
        "status": "Active",
        "incorporation_date": "2019-05-01",
        "roc": "ROC Mumbai",
        "registered_address_latest": "A/304, Third Floor, Jai Tirupati Darshan CHSL, Indralok Phase-3, Bhayander East, Thane, Maharashtra 401105",
        "state": "Maharashtra",
        "postal_code": "401105",
        "authorised_capital_inr": 1000000,
        "paid_up_capital_inr": 100000,
        "latest_turnover_inr": 12168165,
        "turnover_period": "FY2021",
        "latest_net_worth_inr": 1190358,
        "net_worth_period": "FY2021 AOC-4",
        "regulatory_position": None,
        "as_of_date": "2026-01-26",
        "profile_source": SRC["dig_master"],
        "profile_locator": "MCA master-data snapshot, pages 1-2",
        "notes": "FY2021 net worth conflicts across AOC-4 and MGT-7A; see Findings.",
    },
    {
        "company_name": "BAGLAN FARMERS PRODUCER COMPANY LIMITED",
        "cin": "U01100MH2019PTC320804",
        "legal_form": "Producer company limited by shares",
        "status": None,
        "incorporation_date": "2019-02-07",
        "roc": "ROC Mumbai",
        "registered_address_latest": "G No. 100/5, Pimpalgaon Road, Dindori, Chinchkhed, Nashik, Maharashtra 422209",
        "state": "Maharashtra",
        "postal_code": "422209",
        "authorised_capital_inr": 110000,
        "paid_up_capital_inr": 110000,
        "latest_turnover_inr": 229071843,
        "turnover_period": "FY2025",
        "latest_net_worth_inr": 1890890,
        "net_worth_period": "FY2025",
        "regulatory_position": None,
        "as_of_date": "2025-11-17",
        "profile_source": SRC["bag_inc22_25"],
        "profile_locator": "INC-22 XFA fields for office change effective 2025-11-10",
        "notes": "Latest financials are from FY2025 AOC-4. Current MCA master status was not independently checked.",
    },
    {
        "company_name": "DOW CHEMICAL INTERNATIONAL PRIVATE LIMITED",
        "cin": "U24239MH1998PTC113551",
        "legal_form": "Private company limited by shares; Indian non-government; unlisted",
        "status": None,
        "incorporation_date": "1998-02-13",
        "roc": "ROC Mumbai",
        "registered_address_latest": "Unit 201, Building 10, Mindspace IT Park, Plot 3 (Part), TTC Industrial Area MIDC, Thane-Belapur Road, Airoli East, Navi Mumbai, Maharashtra 400708",
        "state": "Maharashtra",
        "postal_code": "400708",
        "authorised_capital_inr": 4220000000,
        "paid_up_capital_inr": 45636590,
        "latest_turnover_inr": 100659719224,
        "turnover_period": "FY2025",
        "latest_net_worth_inr": 14069737233,
        "net_worth_period": "FY2025",
        "regulatory_position": None,
        "as_of_date": "2025-03-31",
        "profile_source": SRC["dow_mgt25"],
        "profile_locator": "MGT-7 XFA fields, FY2025",
        "notes": "Current MCA master status was not independently checked. Annual return reports no penalties/punishments or compounding in FY2025.",
    },
]


financials = []


def fin(company, cin, period, scope, metric, value, source, locator, *, source_unit="INR", normalized=None, confidence=0.98, note=""):
    financials.append({
        "company_name": company,
        "cin": cin,
        "period": period,
        "statement_scope": scope,
        "metric": metric,
        "source_value": value,
        "source_unit": source_unit,
        "normalized_value_inr": value if normalized is None and source_unit == "INR" else normalized,
        "source": source,
        "source_locator": locator,
        "extraction_method": "XFA datasets" if "XFA" in locator else "embedded PDF text + visual page check",
        "confidence": confidence,
        "notes": note,
    })


BAL = ("BALBIR HOLDINGS PRIVATE LIMITED", "U65990MH1996PTC101262")
for period, source, values in [
    ("FY2018", SRC["bal_aoc18"], [("turnover", 2261236), ("profit_before_tax", 393683.51), ("net_worth", 21014500.02), ("paid_up_share_capital", 20000000)]),
    ("FY2019", SRC["bal_aoc19"], [("total_revenue", 2829552), ("profit_before_tax", 819889.83), ("net_worth", 21672345.85), ("tangible_assets", 1260426.22)]),
    ("FY2020", SRC["bal_mgt20"], [("turnover", 3513766.11), ("net_worth", 22247252.06), ("paid_up_share_capital", 20000000)]),
]:
    for metric, value in values:
        fin(*BAL, period, "standalone", metric, value, source, "XFA datasets: annual-return/financial fields")

DIG = ("DIGIVOLUTION CONSULTANCY PRIVATE LIMITED", "U74999MH2019PTC324789")
for metric, value in [
    ("share_capital", 100000), ("reserves_and_surplus", 346039.55), ("trade_payables", 129753.67),
    ("other_current_liabilities", 197962.48), ("short_term_provisions", 466450.53),
    ("total_equity_and_liabilities", 1240207.23), ("total_assets", 1240206.22),
    ("tangible_assets", 193013.60), ("long_term_loans_and_advances", 452000),
    ("trade_receivables", 142520), ("cash_and_bank", 72557.62),
    ("short_term_loans_and_advances", 380115), ("revenue_from_operations", 7729759.66),
    ("other_income", 303335.02), ("total_revenue", 8033094.68),
    ("employee_benefit_expense", 3135960), ("finance_cost", 691.60),
    ("depreciation", 108602.67), ("other_administrative_expenses", 4320219.86),
    ("total_expenses", 7565474.13), ("profit_before_tax", 467620.55),
    ("current_tax", 121581), ("profit_after_tax", 346039.55),
]:
    fin(*DIG, "FY2020", "standalone signed financial statements", metric, value, SRC["dig_fs20"], "PDF pages 1-2; visually verified")
for metric, value in [
    ("total_revenue", 12538165), ("turnover", 12168165), ("profit_before_tax", 1006359),
    ("share_capital", 100000), ("tangible_assets", 142972), ("trade_receivables", 771214),
    ("net_worth", 1190358),
]:
    fin(*DIG, "FY2021", "standalone AOC-4", metric, value, SRC["dig_aoc21"], "XFA datasets: AOC-4 financial fields")
fin(*DIG, "FY2021", "MGT-7A annual return", "turnover", 12538165, SRC["dig_mgt21"], "XFA datasets: TURNOVER")
fin(*DIG, "FY2021", "MGT-7A annual return", "net_worth", 744317, SRC["dig_mgt21"], "XFA datasets: NET_WORTH", note="Conflicts with FY2021 AOC-4 net worth of INR 1,190,358.")

BAG = ("BAGLAN FARMERS PRODUCER COMPANY LIMITED", "U01100MH2019PTC320804")
bag_metrics = {
    "share_capital": (110000, 110000),
    "reserves_and_surplus": (1780890, 1496898),
    "long_term_borrowings": (14000000, 4900000),
    "trade_payables": (54322345, 113111804),
    "short_term_provisions": (431398, 3431764),
    "total_assets": (70644633, 123050466),
    "current_investments": (15128882, 14776444),
    "trade_receivables": (14182571, 25989307),
    "cash_and_cash_equivalents": (1789900, 15218753),
    "short_term_loans_and_advances": (39373765, 59769565),
    "other_current_assets": (169515, 7296397),
    "revenue_from_traded_goods": (229071843, 505831279),
    "interest_income": (541836, 299330),
    "other_non_operating_income": (1353896, 52788137),
    "total_income": (230967575, 558918746),
    "cost_of_material_consumed": (226686598, 506339199),
    "employee_benefit_expense": (1212000, 929200),
    "auditor_payment": (30000, 30000),
    "other_expenses": (2313799, 51065786),
    "total_expenses": (230242397, 558364185),
    "profit_before_tax": (725178, 554561),
    "profit_after_tax": (536631, 410375),
    "net_worth": (1890890, 1606898),
}
for metric, (fy25, fy24) in bag_metrics.items():
    fin(*BAG, "FY2025", "standalone AOC-4", metric, fy25, SRC["bag_aoc25"], "XFA datasets: AOC-4 current-year fields")
    fin(*BAG, "FY2024", "standalone AOC-4 comparative", metric, fy24, SRC["bag_aoc25"], "XFA datasets: AOC-4 previous-year fields")

DOW = ("DOW CHEMICAL INTERNATIONAL PRIVATE LIMITED", "U24239MH1998PTC113551")
dow_metrics = {
    "total_assets": (45460.82, 38358.29),
    "total_equity": (14822.33, 14853.50),
    "revenue_from_operations": (103303.88, 70027.79),
    "total_income": (103494.60, 70298.93),
    "profit_before_tax": (4882.51, 7241.88),
    "profit_after_tax": (3576.70, 5369.30),
    "inventories": (10947.95, 7249.85),
    "trade_receivables": (24178.89, 19798.08),
    "cash_and_cash_equivalents": (2292.52, 3194.43),
    "current_borrowings": (0, 0),
    "non_current_borrowings": (0, 0),
}
for metric, (fy22, fy21) in dow_metrics.items():
    fin(*DOW, "FY2022", "consolidated", metric, fy22, SRC["dow_fs22"], "PDF XBRL instance; values stated in INR million", source_unit="INR million", normalized=fy22 * 1_000_000)
    fin(*DOW, "FY2021", "consolidated comparative", metric, fy21, SRC["dow_fs22"], "PDF XBRL instance; values stated in INR million", source_unit="INR million", normalized=fy21 * 1_000_000)
fin(*DOW, "FY2025", "MGT-7 annual return", "turnover", 100659719224, SRC["dow_mgt25"], "XFA datasets: TURNOVER")
fin(*DOW, "FY2025", "MGT-7 annual return", "net_worth", 14069737233, SRC["dow_mgt25"], "XFA datasets: NET_WORTH")


relationships = []


def rel(company, cin, rel_type, party, identifier, role, start, end, amount, unit, source, locator, notes=""):
    relationships.append({
        "company_name": company, "cin": cin, "relationship_type": rel_type,
        "related_party": party, "related_identifier": identifier, "role_or_basis": role,
        "start_or_event_date": start, "end_date": end, "amount_or_holding": amount,
        "unit": unit, "source": source, "source_locator": locator,
        "extraction_method": "XFA datasets" if "XFA" in locator else "embedded PDF text",
        "confidence": 0.98, "notes": notes,
    })


rel(*BAL, "director", "Philip Chin Peng Chan", "DIN 08452001", "Additional director / promoter", "2019-12-04", None, None, None, SRC["bal_master"], "MCA master-data director table")
rel(*BAL, "director", "Balbirsingh Renu Pritamsingh", "DIN 00227546", "Director", None, None, None, None, SRC["bal_master"], "MCA master-data director table")
rel(*BAL, "director", "Tejinder Singh Renu Balbir Singh", "DIN 01368771", "Director", None, None, None, None, SRC["bal_master"], "MCA master-data director table")
rel(*BAL, "director", "Chanchalsingh Balbirsingh Renu", "DIN 01421713", "Director", None, None, None, None, SRC["bal_master"], "MCA master-data director table")
for party, shares in [("Balbirsingh Renu Pritamsingh", 6500), ("Tejinder Singh Renu Balbir Singh", 0), ("Chanchalsingh Balbirsingh Renu", 489500), ("Philip Chin Peng Chan", 500000)]:
    rel(*BAL, "director_shareholding", party, None, "Director holding at FY2020 year end", "2020-03-31", None, shares, "equity shares", SRC["bal_mgt20"], "XFA datasets: director holding sequence", "Director holdings only; not the complete cap table.")
rel(*BAL, "share_transfer", "Philip Chin Peng Chan", None, "Transferee from Tejinder Singh Renu Balbir Singh", "2019-12-20", None, 494750, "equity shares at INR 10", SRC["bal_mgt20"], "XFA datasets: transfer register")
rel(*BAL, "share_transfer", "Philip Chin Peng Chan", None, "Transferee from Chanchalsingh Balbirsingh Renu", "2019-12-20", None, 5250, "equity shares at INR 10", SRC["bal_mgt20"], "XFA datasets: transfer register")

ADA = ("ADAFOA TECHNOLOGY PRIVATE LIMITED", "U72200DL2022PTC392185")
rel(*ADA, "director", "Ujjwal Singh Rawat", "DIN 09379300", "Director / promoter", "2022-01-07", None, None, None, SRC["ada_master"], "MCA master-data director table")
rel(*ADA, "director", "Ankyit Multani", "DIN 09576717", "Additional director / professional", "2022-04-05", None, None, None, SRC["ada_master"], "MCA master-data director table")
rel(*ADA, "subscriber", "Sufyan Ahmad", None, "MOA subscriber", "2022-01-06", None, 5000, "equity shares", SRC["ada_moa_06"], "XFA datasets: subscriber table")
rel(*ADA, "subscriber", "Ujjwal Singh Rawat", "DIN 09379300", "MOA subscriber", "2022-01-06", None, 5000, "equity shares", SRC["ada_moa_06"], "XFA datasets: subscriber table")

rel(*DIG, "director", "Shilpa Sharma", "DIN 09208927", "Current director in MCA master snapshot", "2022-07-14", None, None, None, SRC["dig_master"], "MCA master-data director table")
rel(*DIG, "director", "Ravendra Kumar", "DIN 09208928", "Current director in MCA master snapshot", "2022-07-14", None, None, None, SRC["dig_master"], "MCA master-data director table")
rel(*DIG, "former_director", "Philip Chin Peng Chan", "DIN 08452001", "Director in FY2020/FY2021 filings", None, "before 2026-01-26 snapshot", None, None, SRC["dig_mgt21"], "XFA datasets: director table")
rel(*DIG, "former_director", "Mayur Sharad Hadkar", "DIN 08440155", "Director and INC-20A/INC-22 signatory", "2019-05-01", "before 2026-01-26 snapshot", None, None, SRC["dig_inc20a"], "XFA datasets: declarant DIN")
rel(*DIG, "auditor", "P.P. Barapatre & Co.", None, "Statutory auditor; Pallavi Barapatre, membership 130916", "2020-03-31", None, None, None, SRC["dig_fs20"], "Signed financial statements, audit report")

rel(*BAG, "director", "Nitendrakumar Singh", "DIN 08103532", "Managing director; AOC-4 signatory", "2025-09-02", None, None, None, SRC["bag_aoc25"], "XFA datasets: signatory block")
rel(*BAG, "director", "Tejas Valuba Aher", "DIN 10597981", "Director; AOC-4 signatory", "2025-09-02", None, None, None, SRC["bag_aoc25"], "XFA datasets: signatory block")
rel(*BAG, "auditor", "Krishnamurthy Jain and Suryawanshi", "FRN 121014W", "Statutory audit firm; signing auditor Punit Shantilal Parmar, membership 164034", "2025-04-01", "2030-03-31", None, None, SRC["bag_adt25"], "XFA datasets: ADT-1 auditor appointment fields")
rel(*BAG, "share_allotment", "Right-issue allottees (aggregate)", None, "PAS-3 allotment", "2024-03-30", None, 1000, "equity shares at INR 10", SRC["bag_pas3"], "XFA datasets: PAS-3 allotment fields", "Post-allotment issued/subscribed/paid-up shares: 11,000; INR 110,000.")

rel(*DOW, "holding_company", "Dow Chemical Pacific (Singapore) Private Limited", "Singapore reg. 199206043M", "Holding company", "2025-03-31", None, 0.5463, "fraction of equity", SRC["dow_mgt25"], "XFA datasets: holding-company fields")
for party, shares in [
    ("Dow Chemical Pacific (Singapore) Pte Ltd", 2493322),
    ("Rohm and Haas Denmark Finance AS", 969962),
    ("Dow Chemical Singapore Holdings Pte Ltd", 17),
    ("Dow Silicones Corporation", 1100358),
]:
    rel(*DOW, "shareholder", party, None, "Equity shareholder", "2023-03-31", None, shares, "equity shares", SRC["dow_sh23"], "Shareholder attachment table")
for party, din in [
    ("Subhash Shriniwas Mukadam", "DIN 03593259"), ("Ragunathan Thangavel", "DIN 06939240"),
    ("Siddhartha Shankar Prasad Ghosal", "DIN 08701099"), ("Vipulkumar Harshadbhai Babu", "DIN 07737345"),
    ("Armin Kurush Daruwalla", "DIN 06499176"), ("Rahul Satish Murdeshwar", "DIN 06906584"),
    ("Manika Bhargava", "DIN 10081611"),
]:
    rel(*DOW, "director", party, din, "Director at FY2025 year end", "2025-03-31", None, None, None, SRC["dow_mgt25"], "XFA datasets: director table")
rel(*DOW, "former_director", "Chandrakant Harishchandra Nayak", "DIN 00680762", "Cessation recorded during FY2025", None, "2024-11-01", None, None, SRC["dow_mgt25"], "XFA datasets: cessation table")


addresses = [
    {"company_name": ADA[0], "cin": ADA[1], "effective_date": "2022-01-07", "address": "House No. 353, Block CB, Naraina Village, South West Delhi, Delhi 110028", "postal_code": "110028", "latitude": None, "longitude": None, "source": SRC["ada_master"], "source_locator": "MCA master-data registered office", "confidence": 0.99, "notes": "Current in master snapshot."},
    {"company_name": BAL[0], "cin": BAL[1], "effective_date": None, "address": "Hotel Pritam Building, Central Avenue, Nagpur, Maharashtra 000000", "postal_code": "000000", "latitude": None, "longitude": None, "source": SRC["bal_master"], "source_locator": "MCA master-data registered office", "confidence": 0.99, "notes": "Postcode conflicts with RBI/FIU-IND official lists."},
    {"company_name": BAL[0], "cin": BAL[1], "effective_date": "2024-12-31", "address": "Hotel Pritam Building, Central Avenue, Nagpur, Maharashtra 440002", "postal_code": "440002", "latitude": None, "longitude": None, "source": RBI_URL, "source_locator": "RBI row 1537, PDF page 29", "confidence": 0.99, "notes": "Same postcode also appears in FIU-IND row 3566."},
    {"company_name": DIG[0], "cin": DIG[1], "effective_date": "2019-05-01", "address": "102, 1st Floor, K-Guru Residency Tower 2, Dharmadas Lane, Borivali West, Mumbai, Maharashtra 400092", "postal_code": "400092", "latitude": None, "longitude": None, "source": SRC["dig_inc20a"], "source_locator": "XFA datasets: INC-20A registered-office fields", "confidence": 0.98, "notes": "Initial address."},
    {"company_name": DIG[0], "cin": DIG[1], "effective_date": "2019-08-06", "address": "B217, Times Square Building, 7th & 8th Floor, Western Express Highway, Andheri East, Mumbai, Maharashtra 400069", "postal_code": "400069", "latitude": None, "longitude": None, "source": SRC["dig_inc22"], "source_locator": "XFA datasets: INC-22 new-office fields", "confidence": 0.98, "notes": "Registered-office change."},
    {"company_name": DIG[0], "cin": DIG[1], "effective_date": None, "address": "A/304, Third Floor, Jai Tirupati Darshan CHSL, Indralok Phase-3, Bhayander East, Thane, Maharashtra 401105", "postal_code": "401105", "latitude": None, "longitude": None, "source": SRC["dig_master"], "source_locator": "MCA master-data registered office", "confidence": 0.99, "notes": "Current in 2026-01-26 master snapshot."},
    {"company_name": BAG[0], "cin": BAG[1], "effective_date": "2019-02-07", "address": "C/o Dilip Nikam, At Mungse, Post Karanjad, Taluka Satana, Nashik, Maharashtra 423301", "postal_code": "423301", "latitude": None, "longitude": None, "source": SRC["bag_inc22_19"], "source_locator": "XFA datasets: INC-22 prior-office fields", "confidence": 0.97, "notes": "Initial/pre-2023 office."},
    {"company_name": BAG[0], "cin": BAG[1], "effective_date": "2023-04-20", "address": "Flat No. 12, Shamkalyan Apartment, Boys Town Road, Nashik, Maharashtra 422001", "postal_code": "422001", "latitude": 19.99779, "longitude": 73.7636, "source": SRC["bag_inc22_23"], "source_locator": "XFA datasets: INC-22 new-office and coordinates fields", "confidence": 0.98, "notes": "Registered-office change."},
    {"company_name": BAG[0], "cin": BAG[1], "effective_date": "2025-11-10", "address": "G No. 100/5, Pimpalgaon Road, Dindori, Chinchkhed, Nashik, Maharashtra 422209", "postal_code": "422209", "latitude": 20.189576, "longitude": 73.939783, "source": SRC["bag_inc22_25"], "source_locator": "XFA datasets: INC-22 new-office and coordinates fields", "confidence": 0.98, "notes": "Latest supplied registered-office change."},
    {"company_name": DOW[0], "cin": DOW[1], "effective_date": "2025-03-31", "address": "Unit 201, Building 10, Mindspace IT Park, Plot 3 (Part), TTC Industrial Area MIDC, Thane-Belapur Road, Airoli East, Navi Mumbai, Maharashtra 400708", "postal_code": "400708", "latitude": 19.16084, "longitude": 73.00127, "source": SRC["dow_mgt25"], "source_locator": "XFA datasets: MGT-7 registered-office fields", "confidence": 0.99, "notes": "Website in annual return: www.dow.in."},
]


regulatory = [
    {
        "company_name": BAL[0], "cin": BAL[1], "authority": "Reserve Bank of India",
        "list_or_register": "List of NBFCs registered with the RBI", "as_of_date": "2024-12-31",
        "status_or_classification": "Registered NBFC; Base layer; ICC; no CoR for holding/accepting public deposits",
        "row_reference": "SR 1537; PDF page 29", "source_url": RBI_URL, "confidence": 0.99,
        "interpretation_limit": "Registration/classification fact only; it is not a shell-company label.",
    },
    {
        "company_name": BAL[0], "cin": BAL[1], "authority": "Financial Intelligence Unit - India",
        "list_or_register": "List of non-compliant NBFCs that had not fulfilled PML Act/Rules obligations relating to FINnet2.0 registration",
        "as_of_date": "2026-02-28", "status_or_classification": "Base-layer NBFC listed as non-compliant for FINnet2.0 registration",
        "row_reference": "Row 3566; PDF page 94", "source_url": FIU_URL, "confidence": 0.99,
        "interpretation_limit": "A dated registration-compliance observation; not an allegation of money laundering and not a shell-company label.",
    },
]


findings = [
    {
        "finding_id": "ADA-OBJ-001", "company_name": ADA[0], "cin": ADA[1],
        "finding_type": "document_content_mismatch", "severity": "medium", "status": "review_required",
        "finding": "The final 2022-01-06 MOA rewrites the main objects toward software/video/skill games, while an 8,299-character ancillary-objects block remains identical across all four MOA versions and contains agriculture, horticulture machinery, agrochemicals, fertilisers and farm language unrelated to the main technology object.",
        "evidence_a": SRC["ada_moa_06"], "locator_a": "XFA datasets: TABLEA3A and TABLEA3B1",
        "evidence_b": SRC["ada_moa_14"], "locator_b": "XFA datasets: TABLEA3A and TABLEA3B1; compared with 2021-12-16 and 2021-12-29 versions",
        "difference_value": None, "difference_unit": None,
        "interpretation_limit": "Possible template/boilerplate inconsistency requiring human review; not evidence of shell status by itself.",
    },
    {
        "finding_id": "DIG-BS-001", "company_name": DIG[0], "cin": DIG[1],
        "finding_type": "filed_statement_arithmetic_mismatch", "severity": "low", "status": "verified",
        "finding": "FY2020 filed balance-sheet total equity and liabilities is INR 1,240,207.23 while total assets is INR 1,240,206.22.",
        "evidence_a": SRC["dig_fs20"], "locator_a": "PDF page 1, visually verified",
        "evidence_b": SRC["dig_fs20"], "locator_b": "PDF page 1, visually verified",
        "difference_value": 1.01, "difference_unit": "INR",
        "interpretation_limit": "Small arithmetic/data-entry inconsistency; materiality and cause are not inferred.",
    },
    {
        "finding_id": "DIG-PBT-002", "company_name": DIG[0], "cin": DIG[1],
        "finding_type": "cross_filing_financial_conflict", "severity": "high", "status": "review_required",
        "finding": "FY2021 AOC-4 previous-period fields report profit before tax of negative INR 7,565,466, conflicting with FY2020 signed financial statements and FY2020 AOC-4 reporting positive profit before tax of about INR 467,621.",
        "evidence_a": SRC["dig_aoc21"], "locator_a": "XFA datasets: PROFIT_BEFORE_PR / PROFIT_BEF_TAX1",
        "evidence_b": SRC["dig_fs20"], "locator_b": "PDF page 2; FY2020 AOC-4 XFA corroboration",
        "difference_value": 8033086.55, "difference_unit": "INR",
        "interpretation_limit": "Cross-filing inconsistency; sign/field mapping or filing error requires manual review.",
    },
    {
        "finding_id": "DIG-NW-003", "company_name": DIG[0], "cin": DIG[1],
        "finding_type": "same_period_net_worth_conflict", "severity": "high", "status": "review_required",
        "finding": "For FY2021, AOC-4 reports net worth of INR 1,190,358 while MGT-7A reports INR 744,317.",
        "evidence_a": SRC["dig_aoc21"], "locator_a": "XFA datasets: NET_WORTH",
        "evidence_b": SRC["dig_mgt21"], "locator_b": "XFA datasets: NET_WORTH",
        "difference_value": 446041, "difference_unit": "INR",
        "interpretation_limit": "Different form definitions or filing error may explain the difference; no fraud inference is made.",
    },
    {
        "finding_id": "BAL-ADDR-001", "company_name": BAL[0], "cin": BAL[1],
        "finding_type": "official_source_address_conflict", "severity": "medium", "status": "review_required",
        "finding": "The MCA master-data PDF shows the Nagpur registered-office postcode as 000000, while both RBI and FIU-IND official lists show 440002 for the same CIN and address.",
        "evidence_a": SRC["bal_master"], "locator_a": "MCA master-data registered office",
        "evidence_b": RBI_URL, "locator_b": "RBI row 1537, PDF page 29; FIU-IND row 3566, PDF page 94",
        "difference_value": None, "difference_unit": None,
        "interpretation_limit": "Likely master-data quality issue; the workbook preserves both observations.",
    },
]


activities = [
    {"company_name": BAL[0], "cin": BAL[1], "period": "FY2020", "activity": "Other financial activities", "activity_code": "K8", "share_of_turnover": None, "source": SRC["bal_mgt20"], "source_locator": "XFA datasets: principal business activity"},
    {"company_name": DIG[0], "cin": DIG[1], "period": "FY2021", "activity": "Management consultancy activities", "activity_code": "M3", "share_of_turnover": None, "source": SRC["dig_mgt21"], "source_locator": "XFA datasets: principal business activity"},
    {"company_name": DOW[0], "cin": DOW[1], "period": "FY2025", "activity": "Chemical manufacturing", "activity_code": None, "share_of_turnover": 0.1839, "source": SRC["dow_mgt25"], "source_locator": "XFA datasets: principal business activity"},
    {"company_name": DOW[0], "cin": DOW[1], "period": "FY2025", "activity": "Wholesale trade", "activity_code": None, "share_of_turnover": 0.7306, "source": SRC["dow_mgt25"], "source_locator": "XFA datasets: principal business activity"},
    {"company_name": DOW[0], "cin": DOW[1], "period": "FY2025", "activity": "Administrative and support services", "activity_code": None, "share_of_turnover": 0.0855, "source": SRC["dow_mgt25"], "source_locator": "XFA datasets: principal business activity"},
]


manifest = []
manifest_path = TMP / "document_manifest.jsonl"
if manifest_path.exists():
    with manifest_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            row["absolute_path"] = ap(f"doc/{row['relative_path']}") if not str(row.get("relative_path", "")).startswith("/") else row["relative_path"]
            manifest.append(row)

company_folder_map = {
    "Adafoa technology Pvt ltd": ADA[0],
    "BALBIR HOLDINGS PRIVATE LIMITED": BAL[0],
    "Digivolution consultancy Pvt lt": DIG[0],
    "BAGLAN FARMERS PRODUCER COMPANY LIMITED-20260803T053634Z-1-001": BAG[0],
    "DOW CHEMICAL INTERNATIONAL PRIVATE LIMITED": DOW[0],
}
for row in manifest:
    folder = str(row.get("company_folder", ""))
    row["company_name"] = company_folder_map.get(folder)

xfa_counts = Counter()
xfa_total_values = 0
xfa_documents = set()
xfa_path = TMP / "xfa/xfa_values.jsonl"
if xfa_path.exists():
    with xfa_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            xfa_total_values += 1
            relpath = str(row.get("relative_path", ""))
            if relpath:
                xfa_documents.add(relpath)
            company = next((name for folder, name in company_folder_map.items() if relpath.startswith(f"{folder}/")), None)
            if company and row.get("packet") == "datasets":
                xfa_counts[company] += 1

doc_counts = Counter(row.get("company_name") for row in manifest if row.get("company_name"))
page_counts = defaultdict(int)
text_page_counts = defaultdict(int)
for row in manifest:
    company = row.get("company_name")
    if not company:
        continue
    page_counts[company] += int(row.get("page_count") or 0)
    text_page_counts[company] += int(row.get("pages_with_text") or 0)

facts = []


def add_fact(cin, company, field_path, value, unit, as_of, source, locator, method, confidence=0.98, notes="", contradiction_group=None):
    facts.append({
        "fact_id": f"F{len(facts)+1:04d}", "cin": cin, "company_name": company,
        "field_path": field_path, "value_text": None if isinstance(value, (int, float)) or value is None else str(value),
        "value_numeric": value if isinstance(value, (int, float)) else None, "unit": unit,
        "as_of_or_period": as_of, "source": source, "source_locator": locator,
        "extraction_method": method, "confidence": confidence, "notes": notes,
        "contradiction_group": contradiction_group,
    })


for c in companies:
    core = [
        ("identity.company_name", c["company_name"], None), ("identity.cin", c["cin"], None),
        ("identity.legal_form", c["legal_form"], None), ("identity.status", c["status"], None),
        ("identity.incorporation_date", c["incorporation_date"], None), ("identity.roc", c["roc"], None),
        ("address.registered_office", c["registered_address_latest"], None),
        ("capital.authorised", c["authorised_capital_inr"], "INR"),
        ("capital.paid_up", c["paid_up_capital_inr"], "INR"),
    ]
    for field, value, unit in core:
        if value is not None:
            add_fact(c["cin"], c["company_name"], field, value, unit, c["as_of_date"], c["profile_source"], c["profile_locator"], "embedded PDF text or XFA datasets")

for f in financials:
    group = None
    if f["cin"] == DIG[1] and f["period"] == "FY2021" and f["metric"] in {"net_worth", "turnover"}:
        group = f"{f['cin']}:{f['period']}:{f['metric']}"
    add_fact(f["cin"], f["company_name"], f"financial.{f['metric']}", f["normalized_value_inr"], "INR", f["period"], f["source"], f["source_locator"], f["extraction_method"], f["confidence"], f["notes"], group)

for r in relationships:
    value = r["related_party"]
    notes = f"{r['relationship_type']}; {r['role_or_basis']}"
    if r["amount_or_holding"] is not None:
        notes += f"; amount/holding={r['amount_or_holding']} {r['unit'] or ''}".rstrip()
    add_fact(r["cin"], r["company_name"], f"relationship.{r['relationship_type']}", value, None, r["start_or_event_date"] or r["end_date"], r["source"], r["source_locator"], r["extraction_method"], r["confidence"], notes)

for a in addresses:
    add_fact(a["cin"], a["company_name"], "address.observation", a["address"], None, a["effective_date"], a["source"], a["source_locator"], "embedded PDF text or XFA datasets", a["confidence"], a["notes"], f"{a['cin']}:registered_address" if a["cin"] == BAL[1] else None)

for r in regulatory:
    add_fact(r["cin"], r["company_name"], f"regulatory.{r['authority'].lower().replace(' ', '_')}", r["status_or_classification"], None, r["as_of_date"], r["source_url"], r["row_reference"], "official regulator PDF text", r["confidence"], r["interpretation_limit"])

coverage = []
for c in companies:
    company = c["company_name"]
    coverage.append({
        "company_name": company, "cin": c["cin"], "documents": doc_counts[company],
        "pdf_pages": page_counts[company], "pages_with_embedded_text": text_page_counts[company],
        "xfa_dataset_values": xfa_counts[company],
        "fact_ledger_rows": sum(1 for f in facts if f["company_name"] == company),
        "financial_rows": sum(1 for f in financials if f["company_name"] == company),
        "relationship_rows": sum(1 for r in relationships if r["company_name"] == company),
        "address_observations": sum(1 for a in addresses if a["company_name"] == company),
        "findings": sum(1 for f in findings if f["company_name"] == company),
    })

payload = {
    "metadata": {
        "title": "Company Intelligence Pilot — 5 Document-Backed Companies",
        "created_date": "2026-08-26",
        "policy": "Only supplied filings and freely accessible official public sources. Missing values are null. No shell-company labels are assigned.",
        "documents_scanned": len(manifest),
        "documents_with_xfa": len(xfa_documents),
        "xfa_values_total": xfa_total_values,
        "xfa_dataset_values": sum(xfa_counts.values()),
        "facts": len(facts),
        "financial_rows": len(financials),
        "relationships": len(relationships),
        "findings": len(findings),
    },
    "companies": companies,
    "financials": financials,
    "relationships": relationships,
    "addresses": addresses,
    "regulatory": regulatory,
    "activities": activities,
    "findings": findings,
    "facts": facts,
    "coverage": coverage,
    "documents": manifest,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: payload["metadata"].get(k) for k in ["documents_scanned", "facts", "financial_rows", "relationships", "findings"]}, indent=2))
print(OUT)
