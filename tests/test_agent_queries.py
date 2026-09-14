import pytest
from agent.agent import AIFraudInvestigator


@pytest.fixture(scope="module")
def agent():
    return AIFraudInvestigator(db_path='data/processed/fraudnet.duckdb')


def test_top_merchants_by_dispute(agent):
    res = agent.investigate('Show top 5 merchants by dispute count')
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0


def test_highest_chargeback_rate_merchants(agent):
    res = agent.investigate('Which merchants have the highest chargeback rate?')
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0


def test_suspicious_fraud_networks(agent):
    res = agent.investigate('Show suspicious fraud networks')
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0


def test_users_connected_multiple_merchants(agent):
    res = agent.investigate('Which users are connected to multiple merchants?')
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0


def test_failed_txns_by_category(agent):
    res = agent.investigate('Show failed transactions by merchant category')
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0


def test_high_risk_merchants_high_gmv(agent):
    res = agent.investigate('Which high-risk merchants have the highest transaction value?')
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0


def test_merchants_unusual_chargeback_rate_with_volume(agent):
    res = agent.investigate('Show merchants with unusually high chargeback rates and sufficient transaction volume')
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0


def test_percentage_failed_txns(agent):
    res = agent.investigate('What percentage of transactions failed?')
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0


def test_total_gmv_query(agent):
    res = agent.investigate('What is the total GMV?')
    assert res['success'] is True
    assert res['df_result'] is not None
    assert len(res['df_result']) > 0


def test_out_of_domain_query_graceful_handling(agent):
    res = agent.investigate('What was the weather during transactions in 1980?')
    assert res['success'] is True or res['success'] is False
    assert res['explanation'] is not None

