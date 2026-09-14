"""
Unit Tests for AI Fraud Investigator Agent
"""

import pytest
from agent.agent import AIFraudInvestigator
from agent.intent import IntentClassifier


def test_intent_classification():
    classifier = IntentClassifier()
    res1 = classifier.classify_intent("Show daily transaction volume trend")
    assert res1['primary_intent'] == 'TREND_ANALYSIS'

    res2 = classifier.classify_intent("Which merchant category has the highest chargeback rate?")
    assert res2['primary_intent'] == 'CATEGORY_ANALYSIS'

    res3 = classifier.classify_intent("Transactions for merchant MCH6613")
    assert res3['entities']['merchant_id'] == 'MCH6613'


def test_agent_end_to_end():
    agent = AIFraudInvestigator()
    res = agent.investigate("Show transaction volume trend over time.")
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0
    assert res['chart_type'] == 'Line Chart'
