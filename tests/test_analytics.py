"""
Unit Tests for Fraud Analytics & KPI Aggregations
"""

import pytest
import pandas as pd
from src.analytics import FraudAnalyticsEngine


def test_kpi_calculations():
    df_tx = pd.DataFrame([
        {'txn_id': 'TXN00000001', 'user_id': 'USR00001', 'merchant_id': 'MCH0001', 'amount': 1000.0, 'status': 'SUCCESS', 'is_utr_missing': False},
        {'txn_id': 'TXN00000002', 'user_id': 'USR00002', 'merchant_id': 'MCH0001', 'amount': 2000.0, 'status': 'FAILED', 'is_utr_missing': True},
        {'txn_id': 'TXN00000003', 'user_id': 'USR00001', 'merchant_id': 'MCH0002', 'amount': 3000.0, 'status': 'PENDING', 'is_utr_missing': False}
    ])
    df_kyc = pd.DataFrame([
        {'user_id': 'USR00001', 'full_name': 'Alice', 'monthly_income': 50000.0, 'kyc_status': 'VERIFIED', 'risk_segment': 'LOW', 'is_synthetic_identity_suspect': False},
        {'user_id': 'USR00002', 'full_name': 'Bob', 'monthly_income': 30000.0, 'kyc_status': 'REJECTED', 'risk_segment': 'HIGH', 'is_synthetic_identity_suspect': True}
    ])
    df_merchants = pd.DataFrame([
        {'merchant_id': 'MCH0001', 'merchant_name': 'Shop A', 'merchant_category': 'Retail', 'merchant_status': 'ACTIVE', 'declared_avg_ticket_size': 1500.0, 'settlement_account': 'ACC1', 'is_shared_settlement_hub': False},
        {'merchant_id': 'MCH0002', 'merchant_name': 'Shop B', 'merchant_category': 'Food', 'merchant_status': 'SUSPENDED', 'declared_avg_ticket_size': 500.0, 'settlement_account': 'ACC1', 'is_shared_settlement_hub': True}
    ])
    df_cbk = pd.DataFrame([
        {'complaint_id': 'CBK0000001', 'txn_id': 'TXN00000001', 'user_id': 'USR00001', 'merchant_id': 'MCH0001', 'disputed_amount': 1000.0, 'severity': 'CRITICAL', 'resolution_status': 'RESOLVED', 'channel': 'IVR'}
    ])

    engine = FraudAnalyticsEngine(df_tx, df_kyc, df_merchants, df_cbk)
    kpis = engine.get_executive_kpis()

    assert kpis['total_transactions'] == 3
    assert kpis['total_gmv'] == 6000.0
    assert kpis['avg_ticket_size'] == 2000.0
    assert kpis['success_transactions'] == 1
    assert kpis['failed_transactions'] == 1
    assert kpis['pending_transactions'] == 1
    assert kpis['total_chargebacks'] == 1
    assert kpis['total_chargeback_amount'] == 1000.0
