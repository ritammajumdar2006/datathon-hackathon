"""
Unit Tests for Fraud Graph Engine
"""

import pytest
import pandas as pd
from src.graph_engine import FraudGraphEngine


def test_graph_network_detection():
    df_tx = pd.DataFrame([
        {'txn_id': 'TXN00000001', 'user_id': 'USR00001', 'merchant_id': 'MCH0001', 'amount': 1000.0, 'status': 'SUCCESS', 'is_utr_missing': False, 'risk_score': 20.0, 'risk_level': 'LOW'},
        {'txn_id': 'TXN00000002', 'user_id': 'USR00002', 'merchant_id': 'MCH0002', 'amount': 5000.0, 'status': 'FAILED', 'is_utr_missing': True, 'risk_score': 80.0, 'risk_level': 'HIGH'}
    ])
    df_kyc = pd.DataFrame([
        {'user_id': 'USR00001', 'full_name': 'Alice', 'kyc_status': 'VERIFIED', 'risk_score': 20.0, 'risk_level': 'LOW', 'is_synthetic_identity_suspect': False},
        {'user_id': 'USR00002', 'full_name': 'Bob', 'kyc_status': 'REJECTED', 'risk_score': 85.0, 'risk_level': 'HIGH', 'is_synthetic_identity_suspect': True}
    ])
    df_merchants = pd.DataFrame([
        {'merchant_id': 'MCH0001', 'merchant_name': 'Shop A', 'merchant_category': 'Retail', 'merchant_status': 'ACTIVE', 'settlement_account': 'ACC_SHARED', 'is_shared_settlement_hub': True, 'risk_score': 40.0, 'risk_level': 'MEDIUM'},
        {'merchant_id': 'MCH0002', 'merchant_name': 'Shop B', 'merchant_category': 'Gaming', 'merchant_status': 'SUSPENDED', 'settlement_account': 'ACC_SHARED', 'is_shared_settlement_hub': True, 'risk_score': 85.0, 'risk_level': 'HIGH'}
    ])
    df_cbk = pd.DataFrame([
        {'complaint_id': 'CBK0000001', 'txn_id': 'TXN00000002', 'user_id': 'USR00002', 'merchant_id': 'MCH0002', 'disputed_amount': 5000.0, 'severity': 'CRITICAL', 'resolution_status': 'OPEN', 'channel': 'Chatbot'}
    ])

    engine = FraudGraphEngine(df_tx, df_merchants, df_kyc, df_cbk)
    networks = engine.detect_suspicious_networks()
    assert len(networks) >= 1
    assert any(n['network_type'] == 'Shared Settlement Collusion Hub' for _, n in networks.iterrows())
