# FRAUDNET AI — Data Governance & Methodology Document

> **TransOrg AgentIQ Datathon — FinTech & BFSI Track**

---

## 1. Amount & Financial Values Governance
- **No `abs()` Transformation**: Negative amounts (e.g. refunds, reversals, OCR negative signs) are preserved as exact negative signed numeric values.
- **Audit Columns**:
  - `amount_raw`: Original string representation as given in the raw file.
  - `amount_clean`: Parsed numeric representation.
  - `negative_amount_flag`: Boolean flag indicating if amount < 0.
  - `invalid_amount_flag`: Boolean flag indicating unparseable values.
  - `amount_parse_status`: Status label (`VALID_PARSED`, `MISSING`, `INVALID_FORMAT`).

---

## 2. Chargeback Disputed Amounts Policy
- **Zero Hallucination / No Arbitrary Imputation**: Missing disputed amounts are **strictly preserved as `NULL`** with `disputed_amount_missing = TRUE`.
- No medians, means, or synthetic estimates are applied to financial loss fields.

---

## 3. Severity Normalization Methodology
- **Text Tiers**:
  - `CRITICAL`, `CRIT` → `CRITICAL`
  - `HIGH`, `H` → `HIGH`
  - `MEDIUM`, `M` → `MEDIUM`
  - `LOW`, `L` → `LOW`
- **Priority Tiers**:
  - `P1` → `CRITICAL` (Urgent regulatory / high financial loss)
  - `P2` → `HIGH` (Account takeover / severe dispute)
  - `P3` → `MEDIUM` (Service dispute / delivery failure)
  - `P4` → `LOW` (Minor amount dispute / customer inquiry)
- Raw values are preserved in `severity_raw` for 100% auditability.

---

## 4. Master Record Conflicts & Survivorship Rules
- **Merchant Master**: Where multiple records share the same normalized `merchant_id`, records are grouped by `conflict_group_id`. The canonical record is selected using the latest `onboarding_date` (`canonical_record_flag = TRUE`).
- **KYC Records**: Where multiple KYC entries exist for the same `user_id`, records are grouped by `conflict_group_id`. The canonical profile is selected using the latest `signup_timestamp` (`canonical_record_flag = TRUE`).

---

## 5. Orphan & Unmatched Records Policy
- Unmatched foreign keys between transactions, merchants, and KYC are flagged:
  - `is_unmatched_merchant`: Transaction merchant not present in `DIM_MERCHANT`.
  - `is_unmatched_kyc`: Transaction user not present in `DIM_CUSTOMER_KYC`.
  - `is_unmatched_transaction`: Chargeback dispute lacking matching transaction record.
- **Rule**: `Unmatched ≠ Fraud`. Orphan records are preserved in the analytical fact tables and are not deleted or blindly labeled as criminal.

---

## 6. Graph Detection & Collusion Criteria
- **Shared Settlement Collusion Hubs**: Subgraphs where $\ge 2$ distinct merchant entities settle into an identical bank account (`settlement_account`).
- **High-Risk Collusion Clusters**: Connected components linking $\ge 4$ entities where $\ge 2$ entities have elevated risk indicators.
- **Labeling**: Flagged entities are categorized as *"Suspicious Network"* / *"Investigation Candidate"* and not asserted as confirmed criminal convictions.
