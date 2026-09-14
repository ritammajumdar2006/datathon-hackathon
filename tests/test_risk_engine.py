"""
Unit Tests for Explainable Risk Engine
"""

import pytest
import pandas as pd
from src.analytics import FraudAnalyticsEngine
from src.risk_engine import ExplainableRiskEngine


def test_risk_scoring():
    df_tx = pd.DataFrame([
        {'txn_id': 'TXN00000001', 'user_id': 'USR00001', 'merchant_id': 'MCH0001', 'amount': 1000.0, 'status': 'SUCCESS', 'is_utr_missing': False},
        {'txn_id': 'TXN00000002', 'user_id': 'USR00002', 'merchant_id': 'MCH0002', 'amount': 22000.0, 'status': 'FAILED', 'is_utr_missing': True}
    ])
    df_kyc = pd.DataFrame([
        {'user_id': 'USR00001', 'full_name': 'Alice', 'monthly_income': 50000.0, 'kyc_status': 'VERIFIED', 'risk_segment': 'LOW', 'is_synthetic_identity_suspect': False},
        {'user_id': 'USR00002', 'full_name': 'Bob', 'monthly_income': 10000.0, 'kyc_status': 'REJECTED', 'risk_segment': 'HIGH', 'is_synthetic_identity_suspect': True}
    ])
    df_merchants = pd.DataFrame([
        {'merchant_id': 'MCH0001', 'merchant_name': 'Shop A', 'merchant_category': 'Retail', 'merchant_status': 'ACTIVE', 'declared_avg_ticket_size': 1000.0, 'settlement_account': 'ACC1', 'is_shared_settlement_hub': False},
        {'merchant_id': 'MCH0002', 'merchant_name': 'Shop B', 'merchant_category': 'Gaming', 'merchant_status': 'SUSPENDED', 'declared_avg_ticket_size': 500.0, 'settlement_account': 'ACC2', 'is_shared_settlement_hub': True}
    ])
    df_cbk = pd.DataFrame([
        {'complaint_id': 'CBK0000001', 'txn_id': 'TXN00000002', 'user_id': 'USR00002', 'merchant_id': 'MCH0002', 'disputed_amount': 22000.0, 'severity': 'CRITICAL', 'resolution_status': 'OPEN', 'channel': 'Chatbot'}
    ])

    analytics = FraudAnalyticsEngine(df_tx, df_kyc, df_merchants, df_cbk)
    df_mch_analytics = analytics.get_merchant_analytics()
    df_user_analytics = analytics.get_user_analytics()

    risk_engine = ExplainableRiskEngine(df_mch_analytics, df_user_analytics, df_tx, df_cbk)
    mch_scored = risk_engine.score_merchants()
    user_scored = risk_engine.score_users()
    tx_scored = risk_engine.score_transactions()

    # Shop B should be HIGH risk due to SUSPENDED status and 100% dispute ratio
    shop_b_score = mch_scored[mch_scored['merchant_id'] == 'MCH0002']['risk_score'].iloc[0]
    assert shop_b_score >= 60.0

    # Bob should be HIGH risk due to REJECTED KYC, synthetic identity suspect, and dispute history
    bob_score = user_scored[user_scored['user_id'] == 'USR00002']['risk_score'].iloc[0]
    assert bob_score >= 60.0

    # Txn 2 should be HIGH risk
    tx2_score = tx_scored[tx_scored['txn_id'] == 'TXN00000002']['risk_score'].iloc[0]
    assert tx2_score >= 60.0
