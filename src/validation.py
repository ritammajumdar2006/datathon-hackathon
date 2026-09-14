"""
FRAUDNET AI - Data Validation & Referential Integrity Module
"""

import pandas as pd
import numpy as np


def validate_referential_integrity(df_tx, df_kyc, df_merchants, df_cbk):
    """
    Validates cross-dataset foreign keys and generates an unmatched record report.
    """
    valid_users = set(df_kyc['user_id'].dropna())
    valid_merchants = set(df_merchants['merchant_id'].dropna())
    valid_txns = set(df_tx['txn_id'].dropna())

    # Transactions validation
    tx_unmatched_users = df_tx[~df_tx['user_id'].isin(valid_users)]
    tx_unmatched_merchants = df_tx[~df_tx['merchant_id'].isin(valid_merchants)]

    # Chargebacks validation
    cbk_unmatched_txns = df_cbk[~df_cbk['txn_id'].isin(valid_txns)]
    cbk_unmatched_users = df_cbk[~df_cbk['user_id'].isin(valid_users)]
    cbk_unmatched_merchants = df_cbk[~df_cbk['merchant_id'].isin(valid_merchants)]

    integrity_summary = {
        'total_transactions': len(df_tx),
        'tx_unmatched_users_count': len(tx_unmatched_users),
        'tx_unmatched_users_pct': round(len(tx_unmatched_users) / max(len(df_tx), 1) * 100, 2),
        'tx_unmatched_merchants_count': len(tx_unmatched_merchants),
        'tx_unmatched_merchants_pct': round(len(tx_unmatched_merchants) / max(len(df_tx), 1) * 100, 2),
        'total_chargebacks': len(df_cbk),
        'cbk_unmatched_txns_count': len(cbk_unmatched_txns),
        'cbk_unmatched_txns_pct': round(len(cbk_unmatched_txns) / max(len(df_cbk), 1) * 100, 2),
        'cbk_unmatched_users_count': len(cbk_unmatched_users),
        'cbk_unmatched_merchants_count': len(cbk_unmatched_merchants),
    }

    return integrity_summary, {
        'tx_unmatched_users': tx_unmatched_users,
        'tx_unmatched_merchants': tx_unmatched_merchants,
        'cbk_unmatched_txns': cbk_unmatched_txns
    }
