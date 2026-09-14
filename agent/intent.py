"""
FRAUDNET AI - Intent Detection & Entity/Metric Extraction
"""

import re


class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            'TREND_ANALYSIS': [r'trend', r'daily', r'monthly', r'over time', r'history', r'timeline', r'last \d+ days'],
            'CATEGORY_ANALYSIS': [r'category', r'mcc', r'merchant category', r'by sector', r'by industry'],
            'MERCHANT_RANKING': [r'top merchant', r'highest chargeback', r'riskiest merchant', r'which merchant', r'merchant with most', r'merchant.*risk'],
            'USER_ANALYSIS': [r'user', r'customer', r'velocity', r'spending', r'top user', r'which user', r'kyc'],
            'NETWORK_INVESTIGATION': [r'cluster', r'ring', r'network', r'collusion', r'graph', r'circle', r'laundering', r'hub'],
            'CHARGEBACK_SUMMARY': [r'chargeback', r'dispute', r'severity', r'reason', r'channel', r'resolution'],
            'GENERAL_METRIC': [r'total', r'how many', r'average', r'kpi', r'gmv', r'count', r'summary', r'overall']
        }

    def classify_intent(self, user_query: str):
        q = user_query.lower()
        matched_intents = []
        for intent, patterns in self.intent_patterns.items():
            for p in patterns:
                if re.search(p, q):
                    matched_intents.append(intent)
                    break
        
        primary_intent = matched_intents[0] if matched_intents else 'GENERAL_METRIC'
        
        # Extract specific entities if present
        mch_match = re.findall(r'MCH[-_\s]?\d+', user_query, re.IGNORECASE)
        user_match = re.findall(r'USR[-_\s]?\d+', user_query, re.IGNORECASE)
        txn_match = re.findall(r'TXN[-_\s]?\d+', user_query, re.IGNORECASE)

        entities = {
            'merchant_id': mch_match[0].upper().replace('-', '').replace(' ', '') if mch_match else None,
            'user_id': user_match[0].upper().replace('-', '').replace(' ', '') if user_match else None,
            'txn_id': txn_match[0].upper().replace('-', '').replace(' ', '') if txn_match else None
        }

        return {
            'query': user_query,
            'primary_intent': primary_intent,
            'entities': entities
        }
