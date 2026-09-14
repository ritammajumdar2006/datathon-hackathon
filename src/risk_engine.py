"""
FRAUDNET AI - Explainable Fraud Risk Engine
TransOrg AgentIQ Datathon - FinTech & BFSI Track
"""

import os
import pandas as pd
import numpy as np


class ExplainableRiskEngine:
    def __init__(self, df_mch_analytics, df_user_analytics, df_tx, df_cbk):
        self.df_mch = df_mch_analytics.copy()
        self.df_user = df_user_analytics.copy()
        self.df_tx = df_tx.copy()
        self.df_cbk = df_cbk.copy()

    def score_merchants(self):
        """
        Calculate transparent, multi-factor merchant risk scores (0-100).
        """
        scores = []
        levels = []
        factor_list = []

        for _, row in self.df_mch.iterrows():
            score = 10.0  # Base line score
            factors = []

            # Factor 1: Chargeback Ratio
            cbk_ratio = row['chargeback_ratio']
            if cbk_ratio >= 25.0:
                score += 35.0
                factors.append(f"Severe chargeback ratio ({cbk_ratio:.1f}%)")
            elif cbk_ratio >= 10.0:
                score += 20.0
                factors.append(f"Elevated chargeback ratio ({cbk_ratio:.1f}%)")
            elif cbk_ratio > 0:
                score += 5.0

            # Factor 2: Merchant Status Anomaly
            status = row['merchant_status']
            if status == 'SUSPENDED':
                score += 25.0
                factors.append("Merchant account currently SUSPENDED")
            elif status == 'INACTIVE' and row['txn_count'] > 0:
                score += 20.0
                factors.append("Active transactions on INACTIVE merchant account")

            # Factor 3: Shared Settlement Collusion Hub
            if row['is_shared_settlement_hub']:
                score += 15.0
                factors.append("Settlement account shared with multiple merchant entities")

            # Factor 4: Ticket Discrepancy (Transaction volume spike)
            disc = row['ticket_discrepancy_ratio']
            if disc >= 3.0 and row['txn_count'] >= 3:
                score += 15.0
                factors.append(f"Average transaction ({row['avg_amount']:.0f}) exceeds declared ticket ({row['declared_avg_ticket_size']:.0f}) by {disc:.1f}x")

            # Factor 5: High-severity disputes
            if row['critical_cbk_count'] >= 2:
                score += 15.0
                factors.append(f"Multiple CRITICAL severity fraud disputes ({row['critical_cbk_count']})")

            # Missing UTR frequency
            if row['txn_count'] > 0 and (row['missing_utr_count'] / row['txn_count']) > 0.3:
                score += 10.0
                factors.append(f"High frequency of missing UTRs ({row['missing_utr_count']}/{row['txn_count']})")

            final_score = min(100.0, max(0.0, round(score, 1)))
            level = 'HIGH' if final_score >= 60 else ('MEDIUM' if final_score >= 35 else 'LOW')

            scores.append(final_score)
            levels.append(level)
            factor_list.append("; ".join(factors) if factors else "Normal operational parameters")

        self.df_mch['risk_score'] = scores
        self.df_mch['risk_level'] = levels
        self.df_mch['risk_factors'] = factor_list
        return self.df_mch

    def score_users(self):
        """
        Calculate transparent, multi-factor user risk scores (0-100).
        """
        scores = []
        levels = []
        factor_list = []

        for _, row in self.df_user.iterrows():
            score = 10.0
            factors = []

            # Factor 1: KYC Status
            kyc_status = row['kyc_status']
            if kyc_status == 'REJECTED':
                score += 30.0
                factors.append("KYC verification REJECTED")
            elif kyc_status == 'PENDING' and row['txn_count'] > 2:
                score += 15.0
                factors.append("High transaction volume on PENDING KYC account")

            # Factor 2: Synthetic Identity Suspicion
            if row['is_synthetic_identity_suspect']:
                score += 25.0
                factors.append("Malformed or unverified PAN and Aadhaar records")

            # Factor 3: Dispute History
            cbk_count = row['chargeback_count']
            if cbk_count >= 3:
                score += 30.0
                factors.append(f"Frequent dispute filer ({cbk_count} chargebacks)")
            elif cbk_count >= 1:
                score += 10.0
                factors.append("History of disputed transactions")

            # Factor 4: Spending vs Declared Income Anomaly
            income_spent = row['income_spent_ratio']
            if income_spent >= 1.5 and row['monthly_income'] > 0:
                score += 15.0
                factors.append(f"Transaction spend ({row['total_spent']:.0f}) exceeds declared monthly income ({row['monthly_income']:.0f})")

            # Factor 5: Risk segment alignment
            if row['risk_segment'] == 'HIGH':
                score += 10.0
                factors.append("Pre-assigned high risk segment")

            final_score = min(100.0, max(0.0, round(score, 1)))
            level = 'HIGH' if final_score >= 60 else ('MEDIUM' if final_score >= 35 else 'LOW')

            scores.append(final_score)
            levels.append(level)
            factor_list.append("; ".join(factors) if factors else "Normal verified account behavior")

        self.df_user['risk_score'] = scores
        self.df_user['risk_level'] = levels
        self.df_user['risk_factors'] = factor_list
        return self.df_user

    def score_transactions(self):
        """
        Score individual transactions based on inherited entity risk and transaction traits.
        """
        mch_risk_map = self.df_mch.set_index('merchant_id')['risk_score'].to_dict()
        user_risk_map = self.df_user.set_index('user_id')['risk_score'].to_dict()
        disputed_txns = set(self.df_cbk['txn_id'].dropna())

        tx_scores = []
        tx_levels = []
        tx_factors = []

        for _, row in self.df_tx.iterrows():
            score = 10.0
            factors = []

            m_score = mch_risk_map.get(row['merchant_id'], 15.0)
            u_score = user_risk_map.get(row['user_id'], 15.0)

            # Inherited entity risk
            if m_score >= 60:
                score += 25.0
                factors.append(f"High-risk merchant ({row['merchant_id']})")
            elif m_score >= 35:
                score += 10.0

            if u_score >= 60:
                score += 25.0
                factors.append(f"High-risk user ({row['user_id']})")
            elif u_score >= 35:
                score += 10.0

            # Missing UTR
            if row['is_utr_missing']:
                score += 20.0
                factors.append("Transaction missing valid UTR number")

            # Dispute link
            if row['txn_id'] in disputed_txns:
                score += 30.0
                factors.append("Transaction flagged in formal chargeback dispute")

            # High value transaction
            if row['amount'] >= 20000:
                score += 15.0
                factors.append(f"High value transaction (₹{row['amount']:,.2f})")

            final_score = min(100.0, max(0.0, round(score, 1)))
            level = 'HIGH' if final_score >= 60 else ('MEDIUM' if final_score >= 35 else 'LOW')

            tx_scores.append(final_score)
            tx_levels.append(level)
            tx_factors.append("; ".join(factors) if factors else "Standard low-risk transaction")

        self.df_tx['risk_score'] = tx_scores
        self.df_tx['risk_level'] = tx_levels
        self.df_tx['risk_factors'] = tx_factors
        return self.df_tx

    def export_scores(self, outputs_dir='outputs'):
        """Export comprehensive fraud scores"""
        os.makedirs(outputs_dir, exist_ok=True)
        mch_scores = self.df_mch[['merchant_id', 'merchant_name', 'merchant_category', 'risk_score', 'risk_level', 'risk_factors']].rename(columns={'merchant_id': 'entity_id', 'merchant_name': 'entity_name'})
        mch_scores['entity_type'] = 'MERCHANT'

        user_scores = self.df_user[['user_id', 'full_name', 'kyc_status', 'risk_score', 'risk_level', 'risk_factors']].rename(columns={'user_id': 'entity_id', 'full_name': 'entity_name'})
        user_scores['entity_type'] = 'USER'

        combined_scores = pd.concat([mch_scores, user_scores], ignore_index=True)
        combined_scores.to_csv(os.path.join(outputs_dir, 'fraud_scores.csv'), index=False)
        return combined_scores
