# FRAUDNET AI - Governed Data Dictionary

## 1. FACT_TRANSACTIONS (track1_upi_transactions.csv)
- txn_id: Normalized transaction ID (TXN%08d), Primary Key.
- timestamp: Harmonized timestamp (TIMESTAMP) with format tracking.
- user_id: Normalized customer ID (USR%05d), Foreign Key to DIM_CUSTOMER_KYC.
- merchant_id: Normalized merchant ID (MCH%04d), Foreign Key to DIM_MERCHANT.
- amount: Signed valid transaction amount (DOUBLE). Preserves exact negative amounts.
- utr: Standardized UTR identifier or UTR_MISSING.
- mcc: 4-digit merchant category code, cross-referenced from merchant master.
- status: Canonical status (SUCCESS, FAILED, PENDING).
- negative_amount_flag: Boolean flag indicating negative financial amount.
- is_unmatched_kyc: Boolean flag indicating orphan user record.
- is_unmatched_merchant: Boolean flag indicating orphan merchant record.

## 2. DIM_CUSTOMER_KYC (track1_kyc_records.csv)
- user_id: Canonical customer ID with latest-timestamp survivorship.
- full_name: Cleaned customer name.
- pan: Masked PAN string (ABXXXXXX1F) with non-destructive format audit.
- aadhaar: Masked Aadhaar string (XXXXXXXX1234) with length validation.
- date_of_birth: Parsed birth timestamp with out-of-range epoch checks.
- monthly_income: Signed monthly income with text stripping and flags.
- kyc_status: Canonical status (VERIFIED, PENDING, REJECTED).
- is_synthetic_identity_suspect: Flag for malformed PAN or Aadhaar.

## 3. DIM_MERCHANT (track1_merchants_master.csv)
- merchant_id: Canonical merchant ID with latest-onboarding survivorship.
- merchant_name: Cleaned merchant business name.
- merchant_category: Canonical industry taxonomy.
- business_type: Standardized legal business classification or UNKNOWN.
- settlement_account: Settlement bank/VPA identifier.
- is_shared_settlement_hub: Flag for accounts linked to multiple merchants.
- declared_avg_ticket_size: Signed declared ticket size with quality flags.

## 4. FACT_CHARGEBACKS (track1_chargebacks.json)
- complaint_id: Canonical dispute identifier (CBK%07d).
- txn_id: Linked transaction identifier (TXN%08d) or unlinked dispute.
- user_id: Normalized customer identifier.
- merchant_id: Normalized merchant identifier.
- disputed_amount: Signed disputed amount; 183 missing values kept strictly NULL.
- disputed_amount_missing: Boolean flag for zero-imputation audit compliance.
- severity: Evidence-based severity rating.
- resolution_status: Canonical status (OPEN, IN_PROGRESS, PENDING_BANK, RESOLVED, REJECTED).
- channel: Customer dispute intake channel (App, Branch, IVR, Chatbot, Call Center, Email).
