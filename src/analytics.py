"""
FRAUDNET AI - Fraud & Merchant Analytics Layer
TransOrg AgentIQ Datathon - FinTech & BFSI Track
"""

import pandas as pd
import numpy as np


class FraudAnalyticsEngine:
    def __init__(self, df_tx, df_kyc, df_merchants, df_cbk):
        self.df_tx = df_tx.copy()
        self.df_kyc = df_kyc.copy()
        self.df_merchants = df_merchants.copy()
        self.df_cbk = df_cbk.copy()

    def get_executive_kpis(self):
        """Calculate high-level executive KPIs"""
        total_tx_count = len(self.df_tx)
        total_gmv = self.df_tx['amount'].sum()
        avg_ticket = self.df_tx['amount'].mean() if total_tx_count > 0 else 0

        success_tx = self.df_tx[self.df_tx['status'] == 'SUCCESS']
        failed_tx = self.df_tx[self.df_tx['status'] == 'FAILED']
        pending_tx = self.df_tx[self.df_tx['status'] == 'PENDING']

        success_rate = (len(success_tx) / total_tx_count * 100) if total_tx_count > 0 else 0
        failed_rate = (len(failed_tx) / total_tx_count * 100) if total_tx_count > 0 else 0

        total_cbk_count = len(self.df_cbk)
        total_cbk_amount = self.df_cbk['disputed_amount'].sum()
        cbk_tx_ratio = (total_cbk_count / total_tx_count * 100) if total_tx_count > 0 else 0
        cbk_gmv_ratio = (total_cbk_amount / total_gmv * 100) if total_gmv > 0 else 0

        active_merchants = self.df_tx['merchant_id'].nunique()
        active_users = self.df_tx['user_id'].nunique()

        return {
            'total_transactions': total_tx_count,
            'total_gmv': round(total_gmv, 2),
            'avg_ticket_size': round(avg_ticket, 2),
            'success_transactions': len(success_tx),
            'success_rate_pct': round(success_rate, 2),
            'failed_transactions': len(failed_tx),
            'failed_rate_pct': round(failed_rate, 2),
            'pending_transactions': len(pending_tx),
            'total_chargebacks': total_cbk_count,
            'total_chargeback_amount': round(total_cbk_amount, 2),
            'chargeback_tx_ratio_pct': round(cbk_tx_ratio, 2),
            'chargeback_gmv_ratio_pct': round(cbk_gmv_ratio, 2),
            'active_merchants': active_merchants,
            'active_users': active_users
        }

    def get_merchant_analytics(self):
        """Aggregate performance & dispute statistics per merchant"""
        # Base merchant dataframe without prior aggregation columns
        base_cols = ['merchant_id', 'merchant_name', 'mcc', 'merchant_category', 'business_type', 'city', 'state', 'onboarding_date', 'settlement_account', 'merchant_status', 'declared_avg_ticket_size', 'is_shared_settlement_hub']
        mch_base = self.df_merchants[[c for c in base_cols if c in self.df_merchants.columns]].drop_duplicates(subset=['merchant_id']).copy()

        # Tx stats
        mch_tx = self.df_tx.groupby('merchant_id').agg(
            txn_count=('txn_id', 'count'),
            total_gmv=('amount', 'sum'),
            avg_amount=('amount', 'mean'),
            failed_count=('status', lambda s: (s == 'FAILED').sum()),
            pending_count=('status', lambda s: (s == 'PENDING').sum()),
            missing_utr_count=('is_utr_missing', 'sum')
        ).reset_index()

        # Chargeback stats
        mch_cbk = self.df_cbk.groupby('merchant_id').agg(
            chargeback_count=('complaint_id', 'count'),
            chargeback_amount=('disputed_amount', 'sum'),
            critical_cbk_count=('severity', lambda s: (s == 'CRITICAL').sum()),
            high_cbk_count=('severity', lambda s: (s == 'HIGH').sum())
        ).reset_index()

        # Merge with master data
        merged = pd.merge(mch_base, mch_tx, on='merchant_id', how='left')
        merged = pd.merge(merged, mch_cbk, on='merchant_id', how='left')

        # Fill NaNs
        merged['txn_count'] = merged['txn_count'].fillna(0).astype(int)
        merged['total_gmv'] = merged['total_gmv'].fillna(0.0)
        merged['avg_amount'] = merged['avg_amount'].fillna(0.0)
        merged['failed_count'] = merged['failed_count'].fillna(0).astype(int)
        merged['missing_utr_count'] = merged['missing_utr_count'].fillna(0).astype(int)
        merged['chargeback_count'] = merged['chargeback_count'].fillna(0).astype(int)
        merged['chargeback_amount'] = merged['chargeback_amount'].fillna(0.0)
        merged['critical_cbk_count'] = merged['critical_cbk_count'].fillna(0).astype(int)
        merged['high_cbk_count'] = merged['high_cbk_count'].fillna(0).astype(int)

        merged['chargeback_ratio'] = np.where(
            merged['txn_count'] > 0,
            (merged['chargeback_count'] / merged['txn_count']) * 100.0,
            0.0
        )
        merged['ticket_discrepancy_ratio'] = np.where(
            merged['declared_avg_ticket_size'] > 0,
            merged['avg_amount'] / merged['declared_avg_ticket_size'],
            1.0
        )

        # Preserve risk scores if already present in input
        if 'risk_score' in self.df_merchants.columns:
            score_map = self.df_merchants.set_index('merchant_id')[['risk_score', 'risk_level', 'risk_factors']].to_dict()
            merged['risk_score'] = merged['merchant_id'].map(lambda x: score_map['risk_score'].get(x, 15.0))
            merged['risk_level'] = merged['merchant_id'].map(lambda x: score_map['risk_level'].get(x, 'LOW'))
            merged['risk_factors'] = merged['merchant_id'].map(lambda x: score_map['risk_factors'].get(x, 'Standard parameters'))

        return merged

    def get_user_analytics(self):
        """Aggregate performance & dispute statistics per user"""
        base_cols = ['user_id', 'full_name', 'pan_masked', 'aadhaar_masked', 'date_of_birth', 'city', 'state', 'monthly_income', 'occupation', 'signup_timestamp', 'kyc_status', 'risk_segment', 'is_synthetic_identity_suspect']
        user_base = self.df_kyc[[c for c in base_cols if c in self.df_kyc.columns]].drop_duplicates(subset=['user_id']).copy()

        user_tx = self.df_tx.groupby('user_id').agg(
            txn_count=('txn_id', 'count'),
            total_spent=('amount', 'sum'),
            avg_spent=('amount', 'mean'),
            failed_count=('status', lambda s: (s == 'FAILED').sum()),
            distinct_merchants=('merchant_id', 'nunique'),
            missing_utr_count=('is_utr_missing', 'sum')
        ).reset_index()

        user_cbk = self.df_cbk.groupby('user_id').agg(
            chargeback_count=('complaint_id', 'count'),
            chargeback_amount=('disputed_amount', 'sum'),
            critical_cbk_count=('severity', lambda s: (s == 'CRITICAL').sum())
        ).reset_index()

        merged = pd.merge(user_base, user_tx, on='user_id', how='left')
        merged = pd.merge(merged, user_cbk, on='user_id', how='left')

        merged['txn_count'] = merged['txn_count'].fillna(0).astype(int)
        merged['total_spent'] = merged['total_spent'].fillna(0.0)
        merged['avg_spent'] = merged['avg_spent'].fillna(0.0)
        merged['failed_count'] = merged['failed_count'].fillna(0).astype(int)
        merged['distinct_merchants'] = merged['distinct_merchants'].fillna(0).astype(int)
        merged['chargeback_count'] = merged['chargeback_count'].fillna(0).astype(int)
        merged['chargeback_amount'] = merged['chargeback_amount'].fillna(0.0)
        merged['critical_cbk_count'] = merged['critical_cbk_count'].fillna(0).astype(int)

        merged['income_spent_ratio'] = np.where(
            merged['monthly_income'] > 0,
            merged['total_spent'] / merged['monthly_income'],
            0.0
        )

        if 'risk_score' in self.df_kyc.columns:
            score_map = self.df_kyc.set_index('user_id')[['risk_score', 'risk_level', 'risk_factors']].to_dict()
            merged['risk_score'] = merged['user_id'].map(lambda x: score_map['risk_score'].get(x, 15.0))
            merged['risk_level'] = merged['user_id'].map(lambda x: score_map['risk_level'].get(x, 'LOW'))
            merged['risk_factors'] = merged['user_id'].map(lambda x: score_map['risk_factors'].get(x, 'Standard parameters'))

        return merged

    def get_category_analytics(self):
        """Aggregate performance by merchant category"""
        df_mch_analytics = self.get_merchant_analytics()
        cat_df = df_mch_analytics.groupby('merchant_category').agg(
            merchant_count=('merchant_id', 'count'),
            total_txns=('txn_count', 'sum'),
            total_gmv=('total_gmv', 'sum'),
            total_chargebacks=('chargeback_count', 'sum'),
            total_disputed_amount=('chargeback_amount', 'sum')
        ).reset_index()

        cat_df['chargeback_ratio'] = np.where(
            cat_df['total_txns'] > 0,
            (cat_df['total_chargebacks'] / cat_df['total_txns']) * 100.0,
            0.0
        )
        cat_df['avg_dispute_amount'] = np.where(
            cat_df['total_chargebacks'] > 0,
            cat_df['total_disputed_amount'] / cat_df['total_chargebacks'],
            0.0
        )
        return cat_df.sort_values(by='total_gmv', ascending=False)
