# FRAUDNET AI - Data Cleaning & Governance Proof Report

## 1. Governance Principles & Strict Constraints
1. Raw data in data/raw/ remains untouched and unmodified (SHA-256 integrity verified).
2. Zero-Imputation Policy: 183 missing disputed amounts remain strictly NULL (disputed_amount_missing=TRUE).
3. Preserved Signed Financial Lineage: No abs() conversion. 429 negative transaction amounts and 501 negative ticket sizes retain exact signs.
4. Deterministic Master Survivorship: Latest-timestamp survivorship applied to 6,114 KYC conflict groups and 1,407 merchant conflict groups.
5. Separation of Data Quality from Fraud: 67.56% unmatched user IDs and 51.92% unmatched merchant IDs classified as Data Quality findings, not fraud.

## 2. Transformation Summary Table
| Dataset | Field | Cleaning Operation | Records Affected | Before Example | After Example |
|---|---|---|---|---|---|
| FACT_TRANSACTIONS | amount | Strip symbols/commas, preserve negative signs | 20,000 | -INR 956.46 | -956.46 (negative_amount_flag=TRUE) |
| FACT_TRANSACTIONS | timestamp | Multi-format parser (ISO/Epoch/Slash) | 20,000 | 1698754800 | 2023-10-31T11:00:00 |
| DIM_CUSTOMER_KYC | pan | Conservative regex validation, UI masking | 28,920 | gewtf5037y | VALID_PAN (UI: GEXXXXXX7Y) |
| DIM_CUSTOMER_KYC | aadhaar | Length validation, UI masking | 28,920 | 089647682915 | VALID_AADHAAR (UI: XXXXXXXX2915) |
| DIM_MERCHANT | settlement_account | Collision detection | 4,343 | EAAS5526551207941 | is_shared_settlement_hub=TRUE (37 Hubs) |
| FACT_CHARGEBACKS | disputed_amount | Zero-imputation preservation | 183 | null / blank | NULL (disputed_amount_missing=TRUE) |
