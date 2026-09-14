"""
FRAUDNET AI - Main AI Fraud Investigator Agent
Pipeline: Question -> Intent -> Query Generation -> Safe Execution -> Chart -> Summary
"""

import re
import duckdb
import pandas as pd
import numpy as np
from agent.intent import IntentClassifier
from agent.query_engine import GovernedQueryEngine
from agent.chart_selector import ChartSelector


class AIFraudInvestigator:
    def __init__(self, db_path='data/processed/fraudnet.duckdb'):
        self.classifier = IntentClassifier()
        self.query_engine = GovernedQueryEngine(db_path)
        self.chart_selector = ChartSelector()

    def generate_analytical_query(self, parsed_intent: dict) -> tuple:
        """
        Translates intent and extracted entities into accurate analytical SQL queries on governed schema.
        """
        intent = parsed_intent['primary_intent']
        entities = parsed_intent['entities']
        query_text = parsed_intent['query'].lower()

        # Specific Entity Lookup
        if entities['merchant_id']:
            m_id = entities['merchant_id']
            sql = f"""
            SELECT txn_id, timestamp, user_id, merchant_id, amount, utr, status
            FROM FACT_TRANSACTIONS
            WHERE merchant_id = '{m_id}'
            ORDER BY timestamp DESC
            LIMIT 50
            """
            title = f"Transactions for Merchant {m_id}"
            return sql, title

        if entities['user_id']:
            u_id = entities['user_id']
            sql = f"""
            SELECT txn_id, timestamp, user_id, merchant_id, amount, utr, status
            FROM FACT_TRANSACTIONS
            WHERE user_id = '{u_id}'
            ORDER BY timestamp DESC
            LIMIT 50
            """
            title = f"Transactions for User {u_id}"
            return sql, title

        # Query Routing by Business Question Patterns
        if "category" in query_text and ("highest" in query_text or "rate" in query_text or "chargeback" in query_text or "dispute" in query_text):
            sql = """
            SELECT m.merchant_category,
                   COUNT(t.txn_id) AS total_transactions,
                   ROUND(SUM(t.amount), 2) AS total_gmv,
                   COUNT(c.complaint_id) AS chargeback_count,
                   ROUND(COUNT(c.complaint_id) * 100.0 / NULLIF(COUNT(t.txn_id), 0), 2) AS chargeback_rate_pct
            FROM FACT_TRANSACTIONS t
            LEFT JOIN DIM_MERCHANT m ON t.merchant_id = m.merchant_id
            LEFT JOIN FACT_CHARGEBACKS c ON t.txn_id = c.txn_id
            WHERE m.merchant_category IS NOT NULL
            GROUP BY m.merchant_category
            HAVING total_transactions >= 10
            ORDER BY chargeback_rate_pct DESC
            LIMIT 15
            """
            title = "Chargeback Rate by Merchant Category"
            return sql, title

        elif intent == 'TREND_ANALYSIS' or 'trend' in query_text or 'volume' in query_text:
            sql = """
            SELECT CAST(timestamp AS DATE) AS transaction_date,
                   COUNT(txn_id) AS transaction_count,
                   ROUND(SUM(amount), 2) AS total_gmv,
                   ROUND(AVG(amount), 2) AS avg_ticket_size
            FROM FACT_TRANSACTIONS
            WHERE timestamp IS NOT NULL
            GROUP BY CAST(timestamp AS DATE)
            ORDER BY transaction_date ASC
            """
            title = "Daily Transaction Volume & GMV Trend"
            return sql, title

        elif "top merchant" in query_text or ("merchant" in query_text and ("highest" in query_text or "disputed" in query_text or "amount" in query_text)):
            sql = """
            SELECT m.merchant_name,
                   m.merchant_category,
                   ROUND(SUM(c.disputed_amount), 2) AS total_disputed_amount,
                   COUNT(c.complaint_id) AS dispute_count
            FROM FACT_CHARGEBACKS c
            JOIN DIM_MERCHANT m ON c.merchant_id = m.merchant_id
            GROUP BY m.merchant_id, m.merchant_name, m.merchant_category
            ORDER BY total_disputed_amount DESC
            LIMIT 10
            """
            title = "Top 10 Merchants by Total Disputed Amount"
            return sql, title

        elif "top user" in query_text or "user" in query_text and ("highest" in query_text or "disputed" in query_text):
            sql = """
            SELECT k.full_name,
                   k.kyc_status,
                   ROUND(SUM(c.disputed_amount), 2) AS total_disputed_amount,
                   COUNT(c.complaint_id) AS dispute_count
            FROM FACT_CHARGEBACKS c
            JOIN DIM_CUSTOMER_KYC k ON c.user_id = k.user_id
            GROUP BY k.user_id, k.full_name, k.kyc_status
            ORDER BY total_disputed_amount DESC
            LIMIT 10
            """
            title = "Top 10 Users by Disputed Amount"
            return sql, title

        elif "severity" in query_text or "channel" in query_text or "reason" in query_text:
            col = "severity" if "severity" in query_text else ("channel" if "channel" in query_text else "reason_code")
            sql = f"""
            SELECT {col},
                   COUNT(complaint_id) AS dispute_count,
                   ROUND(SUM(disputed_amount), 2) AS total_disputed_amount
            FROM FACT_CHARGEBACKS
            GROUP BY {col}
            ORDER BY dispute_count DESC
            """
            title = f"Chargeback Distribution by {col.replace('_', ' ').title()}"
            return sql, title

        elif "success" in query_text or "failed" in query_text or "status" in query_text:
            sql = """
            SELECT status,
                   COUNT(txn_id) AS transaction_count,
                   ROUND(SUM(amount), 2) AS total_amount,
                   ROUND(COUNT(txn_id) * 100.0 / (SELECT COUNT(*) FROM FACT_TRANSACTIONS), 2) AS percentage
            FROM FACT_TRANSACTIONS
            GROUP BY status
            ORDER BY transaction_count DESC
            """
            title = "Transaction Status Breakdown"
            return sql, title

        elif "kyc" in query_text:
            sql = """
            SELECT kyc_status,
                   COUNT(user_id) AS customer_count,
                   ROUND(AVG(monthly_income), 2) AS avg_monthly_income
            FROM DIM_CUSTOMER_KYC
            GROUP BY kyc_status
            ORDER BY customer_count DESC
            """
            title = "Customer KYC Status Breakdown"
            return sql, title

        elif "utr" in query_text:
            sql = """
            SELECT is_utr_missing,
                   COUNT(txn_id) AS txn_count,
                   ROUND(SUM(amount), 2) AS total_gmv,
                   ROUND(AVG(amount), 2) AS avg_amount
            FROM FACT_TRANSACTIONS
            GROUP BY is_utr_missing
            """
            title = "Transactions with Missing vs Valid UTR"
            return sql, title

        # Default: Executive overview metric summary
        sql = """
        SELECT COUNT(t.txn_id) AS total_transactions,
               ROUND(SUM(t.amount), 2) AS total_gmv,
               ROUND(AVG(t.amount), 2) AS avg_ticket_size,
               (SELECT COUNT(*) FROM FACT_CHARGEBACKS) AS total_chargebacks,
               ROUND((SELECT SUM(disputed_amount) FROM FACT_CHARGEBACKS), 2) AS total_disputed_amount
        FROM FACT_TRANSACTIONS t
        """
        title = "Executive Summary Metrics"
        return sql, title

    def investigate(self, user_question: str) -> dict:
        """
        End-to-end execution of investigator inquiry.
        """
        # Step 1 & 2: Intent & Entity extraction
        parsed = self.classifier.classify_intent(user_question)
        
        # Step 3: SQL Generation
        sql_query, title = self.generate_analytical_query(parsed)
        
        # Step 4: Governed Execution
        df_result, err = self.query_engine.execute_safe_query(sql_query)
        if err:
            return {
                'success': False,
                'error': err,
                'sql': sql_query,
                'explanation': "The available dataset does not contain sufficient information to answer this question or query execution failed."
            }

        # Step 5: Visualization Selection & Generation
        fig, chart_type = self.chart_selector.select_and_render_chart(df_result, parsed['primary_intent'], title)

        # Step 6: Text Explanation Synthesis
        summary = self._generate_explanation(df_result, user_question, title)

        return {
            'success': True,
            'intent': parsed['primary_intent'],
            'title': title,
            'sql': sql_query,
            'df_result': df_result,
            'fig': fig,
            'chart_type': chart_type,
            'explanation': summary
        }

    def _generate_explanation(self, df: pd.DataFrame, question: str, title: str) -> str:
        if df.empty:
            return "No records were found matching the analytical criteria."
        
        if df.shape == (1, 1):
            val = df.iloc[0, 0]
            col = df.columns[0]
            formatted_val = f"{val:,.2f}" if isinstance(val, (int, float)) else str(val)
            return f"The computed **{title or col}** is **{formatted_val}** based on the analytical ledger."
        
        if len(df) == 1:
            row_items = [f"**{col.replace('_', ' ').title()}**: {val:,.2f}" if isinstance(val, (int, float)) else f"**{col.replace('_', ' ').title()}**: {val}" for col, val in df.iloc[0].items()]
            return "Key Findings:\n- " + "\n- ".join(row_items)

        # Multi-row insights
        top_row = df.iloc[0]
        first_col = df.columns[0]
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        
        if num_cols:
            metric_col = num_cols[0]
            val = top_row[metric_col]
            formatted_val = f"{val:,.2f}" if isinstance(val, (int, float)) else str(val)
            insight = f"Analysis for **{title}** reveals that **{top_row[first_col]}** ranks highest with **{metric_col.replace('_', ' ').title()}** of **{formatted_val}**."
        else:
            insight = f"Analysis for **{title}** returned **{len(df)}** matching analytical records."

        if len(df) > 1:
            insight += f" (Total entities profiled: **{len(df)}**)."
        return insight
