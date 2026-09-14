# FRAUDNET AI

> **"From Messy UPI Data to Explainable Fraud Intelligence"**
> *Developed for the TransOrg AgentIQ Datathon — FinTech & BFSI Track*

---

## 1. Project Overview & Business Problem

In fast-growing digital payment ecosystems (such as UPI), financial institutions face sophisticated organized fraud vectors:
1. **Circular Money-Laundering & Collusion Rings**: Networks of merchants funneling funds into shared settlement accounts.
2. **Synthetic Identity Fraud**: Compromised or unverified accounts operating with malformed KYC credentials (corrupted PAN / Aadhaar).
3. **Compromised Merchant Accounts**: Suspended or dormant merchants experiencing sudden transaction volume surges followed by severe customer chargebacks.

Raw payment datasets are inherently messy—exhibiting embedded currency symbols (`₹`, `Rs.`, `INR`), OCR character substitutions, mixed Unix epoch and localized timestamp formats, duplicate entries, and fractured entity keys.

**FRAUDNET AI** is an enterprise-grade fraud intelligence command center that transforms messy, raw UPI transaction records into clean, governed, star-schema analytical models, executes multi-factor explainable risk scoring, detects topological graph collusion networks, and equips fraud analysts with an interactive Streamlit dashboard and an Agentic AI Fraud Investigator.

---

## 2. Four Core Datathon Architectural Layers

```
                               ┌──────────────────────────────────────────────┐
                               │             1. DATA RESCUE LAYER             │
                               │  - Deduplication & ID Normalization          │
                               │  - Multi-Currency & Date Harmonization       │
                               │  - Foreign-Key Validation, Relationship      │
                               │    Reconciliation & MCC Standardization      │
                               │  - 12 Comprehensive Audit Governance Reports │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │           2. ANALYTICS & RISK ENGINE         │
                               │  - Governed Star Schema (DuckDB & Parquet)   │
                               │  - Multi-Factor Explainable Scoring (0-100)  │
                               │  - KPI Aggregations & Dispute Velocity       │
                               │  - PII Masking & Privacy Governance          │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │           3. GRAPH-FIRST AI ENGINE           │
                               │  - Heterogeneous NetworkX Entity Graph       │
                               │  - Shared Settlement Collusion Hub Detection │
                               │  - Bipartite High-Risk Cluster Discovery     │
                               │  - Interactive WebGL/Plotly Visualizations   │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │        4. EXECUTIVE DASHBOARD & AGENT        │
                               │  - 8-Page Dark Fintech Command Center        │
                               │  - Real-time Entity Search & Ledger Audit    │
                               │  - Agentic Text-to-Chart AI Investigator     │
                               │  - Read-Only Safe SQL Analytical Router      │
                               └──────────────────────────────────────────────┘
```

---

## 3. Dataset Discovery & Profiling Findings

We strictly preserved all raw data files in `data/raw/` untouched (verified via SHA-256 integrity checks). The profiling of the raw datasets revealed:

| Raw Dataset | Raw Rows | Clean Rows | Duplicate Rows | Key Data Quality Challenges | Governed Resolution Method |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `track1_upi_transactions.csv` | 20,400 | 20,000 | 400 | Currency symbols (`₹`, `Rs.`, `INR`), commas, 429 negative amounts, Unix epoch timestamps, 1,024 missing UTRs | Normalized amounts with exact signed retention (no `abs()`), harmonized timestamps to ISO 8601, flagged missing UTRs |
| `track1_kyc_records.csv` | 36,400 | 28,920 | 278 | 6,114 conflict groups, 7,701 malformed PANs, 6,183 invalid Aadhaar lengths, `k`-notation in income (`27.3k`) | Preserved raw IDs, conservative non-destructive regex flags (`pan_validity_status`), PII masking for UI, latest-signup survivorship |
| `track1_merchants_master.csv` | 6,210 | 4,343 | 12 | 1,407 conflict groups, 15 raw status strings, 40 shared settlement accounts linking 81 merchants | Standardized status (`ACTIVE`, `INACTIVE`, `SUSPENDED`), latest-onboarding survivorship, flagged shared settlement hubs |
| `track1_chargebacks.json` | 2,884 | 2,800 | 84 | 183 missing disputed amounts, 16 raw severity strings, unstructured complaint reasons | Missing disputed amounts are retained as NULL and flagged with disputed_amount_missing = TRUE; they are excluded from disputed-amount aggregation rather than imputed to zero |

---

## 4. Governed Analytical Data Model (Star Schema)

The clean analytical tables are persisted in Apache Parquet format and registered in DuckDB:

1. **`FACT_TRANSACTIONS`**: `txn_id` (PK), `timestamp`, `user_id` (FK), `merchant_id` (FK), `amount_clean` (exact signed value, GMV ₹239,232,643.30), `amount_raw`, `negative_amount_flag`, `invalid_amount_flag`, `utr_raw`, `utr`, `is_utr_missing`, `mcc`, `status`, `is_unmatched_kyc`, `is_unmatched_merchant`.
2. **`DIM_CUSTOMER_KYC`**: `user_id` (PK), `user_id_raw`, `full_name`, `pan_raw`, `pan_normalized`, `pan_validity_status`, `pan_masked`, `aadhaar_raw`, `aadhaar_normalized`, `aadhaar_validity_status`, `aadhaar_masked`, `date_of_birth`, `city`, `state`, `monthly_income`, `occupation`, `signup_timestamp`, `kyc_status`, `conflict_group_id`, `conflict_flag`, `canonical_record_flag`.
3. **`DIM_MERCHANT`**: `merchant_id` (PK), `merchant_id_raw`, `merchant_name`, `mcc`, `merchant_category`, `business_type`, `city`, `state`, `onboarding_date`, `settlement_account`, `merchant_status`, `declared_avg_ticket_size`, `is_shared_settlement_hub`, `conflict_group_id`, `canonical_record_flag`.
4. **`FACT_CHARGEBACKS`**: `complaint_id` (PK), `txn_id` (FK), `user_id` (FK), `merchant_id` (FK), `transaction_timestamp`, `reported_timestamp`, `disputed_amount_clean` (preserves `NULL`s, Total ₹6,790,449.54), `disputed_amount_missing`, `reason_code`, `complaint_text`, `resolution_status`, `bank_response_timestamp`, `severity`, `channel`, `reporting_delay_days`, `is_unmatched_transaction`.

---

## 5. Explainable Multi-Factor Risk Scoring Engine

Every risk score is computed deterministically on a **0 to 100 scale** ($[0, 100]$) with fully documented, transparent audit factors (Explainable Risk Scoring):

### Merchant Risk Score:
- **Base Score**: 10.0
- **Chargeback Ratio**: $+35$ if $\ge 25\%$, $+20$ if $\ge 10\%$, $+5$ if $> 0\%$.
- **Account Status**: $+25$ if `SUSPENDED`, $+20$ if `INACTIVE` with active transaction volume.
- **Shared Settlement Collusion Pattern**: $+15$ if account is pooled across multiple merchant entities.
- **Ticket Surge Discrepancy**: $+15$ if actual average ticket $\ge 3\times$ declared ticket size.
- **Dispute Severity**: $+15$ if $\ge 2$ `CRITICAL` severity disputes.
- **Missing UTR Rate**: $+10$ if $>30\%$ transactions lack valid UTRs.

### User Risk Score:
- **Base Score**: 10.0
- **KYC Compliance**: $+30$ if `REJECTED`, $+15$ if `PENDING` with multiple transactions.
- **Synthetic Identity Suspect**: $+25$ if malformed or unverified PAN and Aadhaar records.
- **Dispute Frequency**: $+30$ if $\ge 3$ chargebacks filed, $+10$ if $\ge 1$.
- **Income-to-Spend Discrepancy**: $+15$ if total transaction spend exceeds declared monthly income.
- **Pre-assigned Segment**: $+10$ if classified in `HIGH` risk segment.

---

## 6. Graph-Based Fraud Detection & Pattern Analysis

Using **NetworkX** and **Plotly**, we construct a heterogeneous bipartite and entity-resolution graph:
- **Nodes**: Users (Circles), Merchants (Squares), Settlement Hubs (Diamonds).
- **Edges**: Transactions (`User` $\to$ `Merchant`), Settlement Links (`Merchant` $\to$ `Settlement Account`).
- **Detected Networks (41 Potential Suspicious Networks)**:
  - **40 Shared Settlement Collusion Hubs (`RING_001` to `RING_040`)**: 40 shared settlement accounts linking 81 distinct merchant entities. Scored at 85.0 (HIGH) due to structural settlement account pooling across legally distinct merchants.
  - **1 High-Risk Interaction Cluster (`RING_041`)**: Dense interaction subgraph connecting 24 users and 11 merchants with 2 flagged high-risk entities.
  - **Signed Financial Integrity in Subgraphs**: `RING_030` preserves its net negative GMV of -₹488.32 derived from exact underlying signed transactions (TXN00014861 +₹7,121.00 and TXN00005480 -₹7,609.32).

---

## 7. Streamlit Executive Command Center (8 Interactive Pages)

1. **📊 Executive Overview**: Reconciled KPI summary (GMV ₹23.92 Cr / ₹239,232,643.30, 20,000 Transactions, 2,800 Disputes, 14.00% Chargeback Rate, 41 Potential Suspicious Networks), daily volume trends, category risk, state distribution, and top flagged entities.
2. **🕸️ 3D Fraud Network**: Interactive 3D WebGL topological graph and Plotly 3D scatter topologies showing settlement account pooling and collusion clusters.
3. **🏢 Merchant Risk Profiler**: Deep dive into individual merchant metrics, declared vs actual ticket sizes, dispute exposure, and multi-factor breakdown.
4. **👤 User Investigation Hub**: Detailed view of high-risk customer profiles, KYC status, synthetic identity flags, and multi-merchant associations.
5. **🗺️ Geographic & Channel Analytics**: Geographic risk heatmaps and channel dispute concentration analysis.
6. **⚖️ Dispute & Chargeback Intelligence**: Chargeback timelines, reporting delay distribution, dispute severity breakdown, and unmapped dispute tracking.
7. **🤖 AI Fraud Investigator**: Conversational analytics interface with governed read-only DuckDB SQL generation, dynamic Plotly chart synthesis, and out-of-domain guardrails.
8. **📋 Data Governance & Audit Trail**: Full transparency tab displaying all 12 generated audit reports and KPI reconciliations.

---

## 8. Agentic Text-to-Chart AI Investigator Architecture

```
USER QUESTION
     │
     ▼
INTENT CLASSIFICATION & ENTITY EXTRACTION
     │
     ▼
GOVERNED SQL QUERY COMPILATION (Read-Only)
     │
     ▼
RESULT VALIDATION & SAFETY GOVERNANCE
     │
     ▼
INTELLIGENT CHART TYPE SELECTION
     ├── Trend over time        ──> Line Chart
     ├── Category comparison    ──> Bar Chart / Horizontal Ranking
     ├── Distribution           ──> Histogram
     ├── Bivariate relationship ──> Scatter Plot
     └── Single metric          ──> Metric KPI Card
     │
     ▼
INTERACTIVE PLOTLY CHART & TEXT SUMMARY
```

---

## 9. Authoritative KPI Reconciliation Summary

| Metric | Definition | Reconciled Value | Governance Status |
| :--- | :--- | :--- | :--- |
| **Total Transactions** | Deduplicated clean UPI transactions | **20,000** | Reconciled (100% Match) |
| **Total GMV** | Sum of valid clean signed amounts (INR) | **₹239,232,643.30** (~₹23.92 Cr) | Reconciled (100% Match) |
| **Success Rate** | Transactions with status = SUCCESS | **85.27%** (17,053 txns) | Reconciled (100% Match) |
| **Failure Rate** | Transactions with status = FAILED | **9.78%** (1,955 txns) | Reconciled (100% Match) |
| **Pending Rate** | Transactions with status = PENDING | **3.86%** (772 txns) | Reconciled (100% Match) |
| **Total Chargebacks** | Deduplicated customer dispute complaints | **2,800** | Reconciled (100% Match) |
| **Total Disputed Exposure** | Sum of clean disputed amounts (retaining NULLs) | **₹6,790,449.54** | Reconciled (100% Match) |
| **Dispute Ratio** | Chargeback count / Transaction count | **14.00%** | Reconciled (100% Match) |
| **High-Risk Users** | Customer profiles with risk_level = HIGH | **847** | Reconciled (100% Match) |
| **High-Risk Merchants** | Merchants with risk_level = HIGH | **352** | Reconciled (100% Match) |
| **Potential Suspicious Networks** | Collusion candidates (40 Hubs + 1 Cluster) | **41** | Reconciled (100% Match) |

---

## 10. Installation & How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run End-to-End Governed Pipeline & Audit Generation
```bash
python run_pipeline.py
```

### Step 3: Run Automated Test Suite
```bash
python -m pytest tests/ -v
```

### Step 4: Launch Interactive Command Center
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501`.

---

## 11. Project Repository Structure

```
fraudnet-ai/
├── data/
│   ├── raw/                           # Untouched raw datathon files
│   │   ├── track1_upi_transactions.csv
│   │   ├── track1_kyc_records.csv
│   │   ├── track1_merchants_master.csv
│   │   ├── track1_chargebacks.json
│   │   └── track1_dataset_notes.txt
│   ├── processed/                     # Governed analytical data layer
│   │   ├── clean_transactions.parquet
│   │   ├── clean_kyc.parquet
│   │   ├── clean_merchants.parquet
│   │   ├── clean_chargebacks.parquet
│   │   └── fraudnet.duckdb
│   └── audit/                         # 12 Official Audit Governance Reports
│       ├── manifest.csv
│       ├── dataset_profile.csv
│       ├── data_quality_report.csv
│       ├── missing_value_report.csv
│       ├── duplicate_report.csv
│       ├── relationship_report.csv
│       ├── id_collision_report.csv
│       ├── kpi_reconciliation.csv
│       ├── dashboard_kpi_reconciliation.csv
│       ├── chargeback_reconciliation.csv
│       ├── transformation_log.csv
│       └── cleaning_proof.csv
├── docs/                              # Datathon Technical Documentation
│   ├── data_dictionary.md
│   ├── data_cleaning_report.md
│   └── final_validation_report.md
├── src/                               # Core pipeline and analytics engines
│   ├── __init__.py
│   ├── transformations.py             # Normalization & parsing functions
│   ├── cleaning.py                    # Reproducible cleaning pipeline
│   ├── analytics.py                   # Single-source-of-truth KPI engine
│   ├── risk_engine.py                 # Explainable multi-factor risk engine
│   ├── graph_engine.py                # Graph pattern & collusion detector
│   └── audit.py                       # Comprehensive audit generation suite
├── agent/                             # Agentic AI Fraud Investigator
│   ├── __init__.py
│   ├── intent.py                      # Intent & entity extraction
│   ├── query_engine.py                # Safe DuckDB query execution
│   ├── chart_selector.py              # Dynamic Plotly chart selector
│   └── agent.py                       # Main orchestrator agent
├── dashboard/                         # Streamlit fintech command center
│   ├── app.py                         # 8-page interactive command center
│   └── styles.py                      # Fintech dark mode custom styling
├── outputs/                           # Exported scores & network ledgers
│   ├── fraud_scores.csv
│   └── suspicious_networks.csv
├── tests/                             # Pytest automated test suite (20 tests)
│   ├── test_cleaning.py
│   ├── test_analytics.py
│   ├── test_risk_engine.py
│   ├── test_graph.py
│   ├── test_agent.py
│   └── test_agent_queries.py
├── run_pipeline.py                    # Master reproducible pipeline runner
├── requirements.txt                   # Deployment dependencies
└── README.md                          # Project documentation
```
