# Company Intelligence Dataset — Data Collection Specification

## 1. Project Goal

Build a high-quality dataset of **10,000+ real companies**, primarily Indian companies, containing both:

- Legitimate operating companies
- Confirmed or strongly evidenced shell / suspicious companies

The dataset will be used to train and evaluate a **machine learning model that detects shell-company behaviour from multiple signals**, rather than relying on a single static rule or field.

The purpose is not simply to classify a company as active or inactive. The model should learn patterns across:

- Corporate records
- Financial behaviour
- Banking / transaction evidence where legally obtainable
- Legal records
- Regulatory actions
- Ownership and director networks
- Addresses
- Tax / compliance indicators
- Related companies
- Business activity
- Historical changes
- Enforcement evidence

---

# 2. Core Principle

Every company in the dataset should look as close as reasonably possible to a **real forensic company profile**.

A company record should not consist only of:

- Company name
- CIN
- Incorporation date
- Active / inactive status

Instead, each record should contain multiple independent categories of evidence that can help distinguish a legitimate operating business from a shell, conduit, dormant, fraudulent, laundering-linked, or otherwise suspicious corporate entity.

---

# 3. Target Dataset Size

## Initial target

- Minimum: **10,000 companies**
- Preferred eventual target: **25,000–100,000+ companies**

## Suggested benchmark set

The existing **15–20 high-quality company examples** should be treated as the initial **Gold Standard / Benchmark Dataset**.

These examples should be analyzed first to determine:

- Required fields
- Optional fields
- Document types
- Evidence depth
- Expected quality
- Missing-data tolerance
- Source quality
- Labeling methodology

No large-scale collection should begin until the benchmark examples have been converted into a common schema.

---

# 4. Dataset Classes

The dataset should not be limited to only two simplistic labels.

Recommended internal labels:

1. `LEGITIMATE`
2. `CONFIRMED_SHELL`
3. `SUSPECTED_SHELL`
4. `DORMANT`
5. `STRUCK_OFF`
6. `FRAUD_LINKED`
7. `MONEY_LAUNDERING_LINKED`
8. `REGULATORY_ACTION`
9. `INSOLVENT`
10. `UNKNOWN / INSUFFICIENT_EVIDENCE`

For ML training, these can later be mapped into:

- Legitimate
- Shell / suspicious

or used as a multiclass model.

---

# 5. Ground-Truth Requirement

The collection agents must **never invent whether a company is a shell company**.

A label must be based on evidence.

Examples of acceptable evidence:

- Court judgment
- Enforcement Directorate investigation
- SFIO investigation
- SEBI order
- RBI-related enforcement record
- MCA action
- Income Tax investigation disclosed in public proceedings
- CBI investigation
- NCLT / NCLAT proceedings
- Official government notification
- Charge sheet or prosecution record
- Judicial findings
- Regulatory order
- Official strike-off action
- Credible public disclosures supported by primary sources

Every label should contain:

```text
label
label_confidence
label_reason
label_source
label_source_date
label_verified
```

---

# 6. Required Company Identity Data

Each company should contain, wherever available:

```text
company_name
legal_name
previous_names
cin
registration_number
company_status
company_class
company_category
company_subcategory
incorporation_date
roc
registered_state
registered_city
registered_address
postal_code
email
website
listed_status
stock_exchange
industry
nic_code
business_description
```

---

# 7. Capital and Corporate Structure

Collect:

```text
authorized_capital
paid_up_capital
share_capital_history
number_of_shareholders
shareholding_structure
promoters
beneficial_owners
ultimate_beneficial_owners
holding_company
subsidiaries
associate_companies
related_entities
foreign_parent
foreign_subsidiaries
```

Where historical information is available, retain the history rather than overwriting old values.

---

# 8. Directors and Key Personnel

For every company collect:

```text
directors
past_directors
director_din
director_appointment_date
director_resignation_date
director_disqualification_status
director_other_companies
director_network_size
key_managerial_personnel
authorized_signatories
auditors
past_auditors
company_secretary
```

The dataset should enable graph analysis such as:

```text
Company -> Director -> Other Company
Company -> Auditor -> Other Company
Company -> Address -> Other Company
Company -> Shareholder -> Other Company
```

---

# 9. Address Intelligence

Addresses are particularly important for shell-company detection.

Collect:

```text
registered_address
operating_addresses
previous_addresses
address_change_history
address_type
geo_location_if_available
number_of_companies_at_same_address
companies_sharing_address
residential_vs_commercial_indicator
virtual_office_indicator
address_verification_status
```

Potential suspicious indicators include:

- Hundreds of companies at one small address
- Frequent registered-office changes
- Residential address used by many unrelated companies
- Address inconsistent with claimed business scale

These are **signals**, not automatic proof of shell activity.

---

# 10. Financial Statements

Where legally and publicly obtainable, collect:

```text
financial_year
revenue
operating_revenue
other_income
total_income
profit_before_tax
profit_after_tax
ebitda
total_assets
current_assets
fixed_assets
cash_and_cash_equivalents
inventory
trade_receivables
loans_and_advances
investments
total_liabilities
short_term_debt
long_term_debt
trade_payables
net_worth
reserves
share_capital
cash_flow_from_operations
cash_flow_from_investing
cash_flow_from_financing
```

Also derive ratios such as:

```text
revenue_to_assets
cash_to_assets
debt_to_equity
receivable_days
payable_days
asset_turnover
profit_margin
current_ratio
related_party_transaction_ratio
```

---

# 11. Bank and Transaction Data

Raw private bank-account transaction data for ordinary companies will generally **not be publicly available**.

Agents must never fabricate transactions.

Transaction information should only be collected when it appears legally in public sources such as:

- Court judgments
- Enforcement orders
- ED proceedings
- SEBI orders
- SFIO reports
- Charge sheets
- Public insolvency records
- Regulatory proceedings
- Published forensic reports
- Publicly released investigation documents

Possible transaction fields:

```text
transaction_date
transaction_amount
currency
sender_entity
receiver_entity
sender_bank_if_public
receiver_bank_if_public
account_reference_if_legally_public
transaction_type
transaction_description
transaction_source_document
transaction_source_page
transaction_confidence
```

---

# 12. Transaction Behaviour Features

Where transaction evidence exists, derive patterns such as:

```text
high_value_transactions
rapid_in_out_transactions
circular_transactions
round_number_transactions
same_day_in_out
layering_pattern
multiple_related_party_transfers
unexplained_loans
large_unsecured_loans
cash_intensive_activity
foreign_transfers
high_risk_jurisdiction_links
transaction_velocity
transaction_network_depth
```

These features should be derived from evidence, not guessed.

---

# 13. Tax and Compliance Data

Where publicly available:

```text
gstin
gst_status
gst_registration_date
gst_cancellation
tax_default_mentions
income_tax_action
tds_related_action
tax_litigation
filing_compliance
annual_return_status
financial_statement_filing_status
late_filings
non_filings
compliance_history
```

---

# 14. MCA / ROC Filings

Collect relevant filings and metadata such as:

```text
annual_returns
financial_statements
director_changes
registered_office_changes
share_allotments
charge_creation
charge_modification
charge_satisfaction
auditor_changes
company_name_changes
object_clause_changes
merger_filings
strike_off_filings
restoration_filings
```

For each document:

```text
document_type
document_date
filing_date
source
document_url_or_reference
extracted_fields
extraction_confidence
```

---

# 15. Charges, Loans and Security

Collect:

```text
charges
charge_holder
charge_amount
charge_creation_date
charge_modification_date
charge_satisfaction_date
secured_lender
loan_type
collateral_description
outstanding_charge_status
```

Potential signals:

- Very large loans relative to business activity
- Repeated charge creation and satisfaction
- Multiple related lenders
- Unsecured loans from connected parties

---

# 16. Legal Proceedings

Collect all relevant public legal information:

```text
court_name
case_number
case_title
case_type
filing_date
decision_date
company_role
opposing_party
legal_issue
allegations
court_findings
outcome
penalty
damages
case_status
judgment_source
```

Relevant forums may include:

- Supreme Court of India
- High Courts
- District courts where accessible
- NCLT
- NCLAT
- SAT
- Special PMLA courts
- Other regulatory tribunals

---

# 17. Enforcement and Regulatory Records

Search for every company across:

- Ministry of Corporate Affairs
- Registrar of Companies
- Serious Fraud Investigation Office
- Enforcement Directorate
- Securities and Exchange Board of India
- Reserve Bank of India
- Central Bureau of Investigation
- Income Tax Department
- GST authorities
- Competition Commission of India
- NCLT
- NCLAT
- Courts
- State police / EOW records where publicly available

Fields:

```text
agency
action_type
action_date
allegation
amount_involved
persons_involved
related_companies
law_or_section
case_reference
status
final_outcome
source
```

---

# 18. Related-Party Transactions

Collect where available:

```text
related_party
relationship_type
transaction_type
transaction_amount
transaction_year
loan
advance
purchase
sale
guarantee
investment
director_related_transaction
promoter_related_transaction
```

---

# 19. Ownership Network

The system should identify:

```text
direct_shareholders
indirect_shareholders
beneficial_owners
ultimate_beneficial_owner
promoters
nominee_shareholders
corporate_shareholders
foreign_shareholders
common_shareholders
cross_holdings
```

Graph relationships should be retained.

---

# 20. Company Network / Graph Dataset

In addition to a flat table, create a graph representation.

## Example nodes

```text
Company
Director
Shareholder
Beneficial Owner
Bank
Address
Auditor
Court Case
Regulator
Transaction
Loan
Subsidiary
Foreign Entity
```

## Example edges

```text
DIRECTOR_OF
SHAREHOLDER_OF
OWNS
CONTROLLED_BY
REGISTERED_AT
SHARES_ADDRESS_WITH
AUDITED_BY
TRANSFERRED_TO
TRANSFERRED_FROM
SUBSIDIARY_OF
RELATED_TO
INVESTIGATED_BY
ACCUSED_IN
PARTY_TO_CASE
BORROWED_FROM
LENT_TO
```

This graph may become one of the strongest components of the shell-company detection system.

---

# 21. Shell-Company Signals

The model should be able to learn combinations of signals such as:

### Corporate

- Frequent director changes
- Common directors across many entities
- Very short director tenures
- Disqualified directors
- Nominee-like director patterns
- Multiple entities controlled by same small group

### Address

- Many companies sharing one address
- Repeated address changes
- Residential / questionable registered office
- Address inconsistent with stated operations

### Financial

- Very low revenue but high transaction activity
- Large loans without operating activity
- High related-party transactions
- Large receivables / payables without matching operations
- Sudden revenue spikes
- Unusual asset growth
- Minimal fixed assets
- Continuous losses while large money flows continue

### Transaction

- Circular fund movement
- Layering
- Rapid incoming and outgoing transfers
- Large round-number transfers
- Same entities repeatedly transferring funds
- No apparent commercial justification

### Legal / Regulatory

- ED / SFIO / SEBI / CBI involvement
- Tax-evasion allegations
- Money-laundering proceedings
- Fraud proceedings
- Repeated strike-off / restoration events
- Regulatory penalties

### Network

- Connected to known shell companies
- Shared directors with sanctioned / investigated companies
- Shared addresses with numerous suspicious companies
- Multiple layers of ownership without obvious economic purpose

No single signal should automatically determine the label.

---

# 22. Evidence Requirement

Every extracted field should ideally contain provenance.

Recommended structure:

```json
{
  "value": "...",
  "source": "...",
  "source_type": "...",
  "source_date": "...",
  "source_reference": "...",
  "retrieved_at": "...",
  "confidence": 0.0
}
```

This allows auditing and prevents the dataset from becoming contaminated with hallucinated information.

---

# 23. Source Priority

Agents should prioritize sources in roughly this order:

## Tier 1 — Primary / Official

- MCA / ROC
- Courts
- NCLT / NCLAT
- SEBI
- RBI
- ED
- SFIO
- CBI
- Income Tax Department
- GST authorities
- Official gazettes
- Stock exchanges
- Company annual reports

## Tier 2 — High-quality structured sources

- Government open-data portals
- Exchange disclosures
- Public insolvency records
- Official company websites

## Tier 3 — Secondary research

- Reputable financial newspapers
- Reputable legal databases
- Investigative journalism
- Industry databases

Tier 3 sources should normally be used as leads and independently verified whenever possible.

---

# 24. AI Agent Architecture

A multi-agent collection system can be used.

## Agent 1 — Company Discovery Agent

Responsibilities:

- Identify candidate companies
- Retrieve company identifiers
- Avoid duplicates
- Create initial company queue

## Agent 2 — Corporate Registry Agent

Collect:

- MCA / ROC data
- Incorporation
- Directors
- Capital
- Status
- Filings
- Charges

## Agent 3 — Financial Agent

Collect and normalize:

- Financial statements
- Ratios
- Annual reports
- Revenue / assets / liabilities
- Financial anomalies

## Agent 4 — Legal Agent

Search:

- Court cases
- NCLT
- NCLAT
- Judgments
- Litigation history

## Agent 5 — Enforcement Agent

Search:

- ED
- SEBI
- SFIO
- CBI
- RBI
- Tax enforcement
- Government proceedings

## Agent 6 — Network Intelligence Agent

Build:

- Director networks
- Shared addresses
- Common shareholders
- Related entities
- Corporate ownership trees

## Agent 7 — Transaction Evidence Agent

Search public legal and regulatory records for transaction details.

It must never invent private banking data.

## Agent 8 — Document Extraction Agent

Read:

- PDFs
- Annual reports
- Court judgments
- Orders
- Regulatory documents

Extract structured facts and preserve page references.

## Agent 9 — Verification Agent

Independently verify important facts.

Check:

- Identity
- Labels
- Financial numbers
- Directors
- Legal allegations
- Transactions
- Regulatory actions

## Agent 10 — Quality Control Agent

Determine whether the company meets the dataset standard.

Possible statuses:

```text
COMPLETE
PARTIALLY_COMPLETE
INSUFFICIENT_DATA
REQUIRES_MANUAL_REVIEW
REJECTED
```

---

# 25. Agent Rule: Evidence, Not Conclusions

Agents should behave as researchers, not storytellers.

They must:

- Extract facts
- Save sources
- Record uncertainty
- Preserve conflicting information
- Avoid guessing
- Avoid fabricating missing values
- Never manufacture bank transactions
- Never call a company a shell without evidence

Missing fields should remain:

```text
null
```

and not be filled with AI-generated guesses.

---

# 26. Company Record Completeness Score

Each company can receive a completeness score.

Example:

| Category | Weight |
|---|---:|
| Identity | 10 |
| Directors | 10 |
| Ownership | 10 |
| Address | 5 |
| Financials | 15 |
| MCA filings | 10 |
| Legal records | 10 |
| Regulatory records | 10 |
| Transactions | 10 |
| Network intelligence | 5 |
| Label evidence | 5 |

Total:

```text
100
```

Example acceptance threshold:

```text
>= 70 = Training-quality
50–69 = Partial / research queue
< 50 = Insufficient
```

The actual threshold should be calibrated using the existing benchmark companies.

---

# 27. Data Quality Score

Separate from completeness, each record should have a quality score based on:

```text
source_quality
source_count
cross_source_confirmation
extraction_confidence
data_recency
document_availability
identity_confidence
label_confidence
```

A company having lots of data does not necessarily mean the data is reliable.

---

# 28. Preventing Data Leakage

The dataset must distinguish between:

## Features

Information available to the model.

## Label evidence

Information used to establish the ground-truth classification.

For example, if an ED order explicitly says:

> Company X was used as a shell entity.

that statement may establish the label.

But if the same ED statement is directly fed as an input feature during training, the model may simply learn keywords such as "shell company" instead of learning underlying corporate behaviour.

Therefore maintain:

```text
feature_data
label_evidence
```

as separate components.

---

# 29. Time-Aware Dataset

Where possible, preserve dates.

The system should eventually support questions such as:

> Could the model have identified the company as suspicious before regulators publicly identified it?

Therefore retain historical snapshots:

```text
company_state_at_date
directors_at_date
financials_for_year
address_at_date
network_at_date
regulatory_event_date
```

This enables a much stronger predictive model than using only current-state data.

---

# 30. Storage Format

Recommended architecture:

## Raw Evidence Layer

Original:

- PDFs
- HTML
- CSV
- JSON
- filings
- judgments
- orders

## Normalized Company Layer

One structured record per company.

Possible formats:

```text
JSON
JSONL
Parquet
SQL
```

## Graph Layer

Use a graph database or graph-compatible representation for relationships.

## ML Feature Layer

Contains cleaned features used directly for training.

---

# 31. Suggested Company JSON Structure

```json
{
  "company_id": "",
  "identity": {},
  "corporate_status": {},
  "addresses": [],
  "directors": [],
  "shareholders": [],
  "beneficial_owners": [],
  "financials": [],
  "banking_evidence": [],
  "transactions": [],
  "charges": [],
  "legal_cases": [],
  "regulatory_actions": [],
  "tax_compliance": {},
  "related_parties": [],
  "company_network": {},
  "documents": [],
  "risk_signals": [],
  "label": {},
  "quality": {},
  "sources": []
}
```

---

# 32. Benchmark Phase

Before attempting 10,000 companies:

## Step 1

Provide the existing document describing required company documents.

## Step 2

Provide the 15–20 example company datasets.

## Step 3

Reverse-engineer them into:

```text
MASTER_SCHEMA.json
FIELD_DICTIONARY.md
SOURCE_MAP.md
LABELING_GUIDE.md
QUALITY_RULES.md
```

## Step 4

Run the collection pipeline on approximately:

```text
20–50 new companies
```

## Step 5

Compare automatically collected records against the Gold Standard.

## Step 6

Fix missing fields, extraction errors, source problems and labeling problems.

## Step 7

Scale to:

```text
100
500
1,000
10,000+
```

Only scale once quality remains stable.

---

# 33. Definition of a Dataset-Ready Company

A company should enter the final training dataset only when:

- Identity is verified.
- Duplicate identity has been ruled out.
- Required core fields have been collected.
- Sources are stored.
- Important facts have provenance.
- Missing information is explicitly marked.
- Legal/regulatory allegations distinguish allegation from final finding.
- Label evidence meets the defined standard.
- Verification agent has reviewed the record.
- Quality-control rules have passed.
- No material information has been fabricated.

---

# 34. Primary Objective

The end product should not simply be:

```text
10,000 company names
```

It should be:

> **10,000 evidence-backed, machine-readable corporate intelligence profiles with enough financial, legal, ownership, network, compliance, and behavioural information to train and evaluate a model for identifying shell-company patterns.**

Quality is more important than reaching 10,000 quickly.

The benchmark companies define what "good" looks like.

The agent system should reproduce that standard at scale.
