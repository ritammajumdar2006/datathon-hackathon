"""
FRAUDNET AI - Master Reproducible Pipeline Runner
Executes:
1. Raw Data Ingestion & Manifest Check
2. Governed Data Cleaning & Star Schema Parquet/DuckDB Creation
3. Referential Integrity & Validation Audits
4. Analytics & Financial KPI Profiling
5. Multi-Factor Explainable Risk Scoring
6. Graph Collusion & Shared Settlement Hub Detection
7. Complete Audit Suite Generation (data/audit/)
"""

import sys
import time
from src.cleaning import CleaningPipeline
from src.analytics import FraudAnalyticsEngine
from src.risk_engine import ExplainableRiskEngine
from src.graph_engine import FraudGraphEngine
from src.audit import ComprehensiveAuditEngine


def main():
    print("=" * 70)
    print("  FRAUDNET AI: 100% DATA-GROUNDED REPRODUCIBLE PIPELINE")
    print("  TransOrg AgentIQ Datathon — FinTech & BFSI Track")
    print("=" * 70)

    start_time = time.time()

    # Step 1: Run Cleaning & Transformation Pipeline
    print("\n[STEP 1/5] Executing Governed Data Cleaning Pipeline...")
    cleaning_pipeline = CleaningPipeline(
        raw_dir='data/raw',
        processed_dir='data/processed',
        outputs_dir='outputs'
    )
    df_tx, df_kyc, df_merchants, df_cbk = cleaning_pipeline.run_pipeline()
    print(f" -> Clean Transactions: {len(df_tx):,} records (GMV: INR {df_tx['amount_clean'].sum():,.2f})")
    print(f" -> Clean KYC Master:   {len(df_kyc):,} canonical user profiles")
    print(f" -> Clean Merchants:    {len(df_merchants):,} canonical merchants")
    print(f" -> Clean Chargebacks:  {len(df_cbk):,} disputes (Total: INR {df_cbk['disputed_amount_clean'].dropna().sum():,.2f})")

    # Step 2: Financial Analytics & KPI Engine
    print("\n[STEP 2/5] Computing Analytics & Reconciled KPIs...")
    analytics_engine = FraudAnalyticsEngine(df_tx, df_kyc, df_merchants, df_cbk)
    kpis = analytics_engine.get_executive_kpis()
    print(f" -> Reconciled GMV:        INR {kpis['total_gmv']:,.2f}")
    print(f" -> Success Rate:          {kpis['success_rate_pct']:.2f}% ({kpis['success_transactions']:,} txns)")
    print(f" -> Failure Rate:          {kpis['failed_rate_pct']:.2f}% ({kpis['failed_transactions']:,} txns)")
    print(f" -> Chargeback Ratio:      {kpis['chargeback_tx_ratio_pct']:.2f}% ({kpis['total_chargebacks']:,} disputes)")

    # Step 3: Explainable Risk Scoring Engine
    print("\n[STEP 3/5] Computing Explainable Multi-Factor Risk Scores (0-100)...")
    df_mch_analytics = analytics_engine.get_merchant_analytics()
    df_user_analytics = analytics_engine.get_user_analytics()
    risk_engine = ExplainableRiskEngine(df_mch_analytics, df_user_analytics, df_tx, df_cbk)
    risk_engine.score_merchants()
    risk_engine.score_users()
    risk_engine.score_transactions()
    df_scores = risk_engine.export_scores(outputs_dir='outputs')
    high_risk_count = (df_scores['risk_level'] == 'HIGH').sum()
    print(f" -> Scored {len(df_scores):,} entities | High Risk Entities: {high_risk_count:,}")

    # Step 4: Graph Collusion & Shared Settlement Hub Detection
    print("\n[STEP 4/5] Constructing Heterogeneous Entity Graph & Collusion Rings...")
    graph_engine = FraudGraphEngine(df_tx, df_merchants, df_kyc, df_cbk)
    df_networks = graph_engine.detect_suspicious_networks(outputs_dir='outputs')
    shared_hubs = df_merchants['is_shared_settlement_hub'].sum()
    print(f" -> Discovered {len(df_networks)} Suspicious Collusion Networks")
    print(f" -> Identified {shared_hubs} Merchants linked across Shared Settlement Hub Accounts")

    # Step 5: Comprehensive Audit Suite
    print("\n[STEP 5/5] Generating Data Governance & Audit Reports...")
    audit_engine = ComprehensiveAuditEngine(
        raw_dir='data/raw',
        processed_dir='data/processed',
        audit_dir='data/audit',
        outputs_dir='outputs'
    )
    audit_engine.run_full_audit()

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"  ALL PIPELINE STAGES EXECUTED SUCCESSFULLY in {elapsed:.2f}s")
    print("  Run 'streamlit run dashboard/app.py' to explore the command center.")
    print("=" * 70)


if __name__ == '__main__':
    main()
