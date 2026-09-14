"""
FRAUDNET AI - Governed DuckDB Query Engine with Safety Safeguards
"""

import duckdb
import pandas as pd
import numpy as np


class GovernedQueryEngine:
    def __init__(self, db_path='data/processed/fraudnet.duckdb'):
        self.db_path = db_path

    def get_connection(self):
        return duckdb.connect(self.db_path, read_only=True)

    def execute_safe_query(self, sql_query: str):
        """
        Executes read-only analytical SQL with strict injection and destruction safeguards.
        """
        forbidden_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'REPLACE', 'CREATE', 'ATTACH', 'DETACH']
        clean_sql = sql_query.strip()
        
        for kw in forbidden_keywords:
            if re_match := kw in clean_sql.upper().split():
                return None, f"Security Exception: Modifying keyword '{kw}' is strictly prohibited."

        try:
            conn = self.get_connection()
            df_result = conn.execute(clean_sql).df()
            conn.close()
            return df_result, None
        except Exception as e:
            return None, f"Query Execution Error: {str(e)}"
