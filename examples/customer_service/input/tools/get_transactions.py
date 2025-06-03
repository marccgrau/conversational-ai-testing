from typing import Any, Dict

import pandas as pd
from langchain.tools import StructuredTool


class GetTransactions:
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        account_id: str,
        date_from: str = None,
        date_to: str = None,
    ) -> str:
        tx_df: pd.DataFrame = data["transactions"]
        tx_df = tx_df[tx_df["account_id"] == account_id]
        if date_from:
            tx_df = tx_df[tx_df["date"] >= date_from]
        if date_to:
            tx_df = tx_df[tx_df["date"] <= date_to]
        if tx_df.empty:
            return "Error: no transactions for supplied criteria"
        return tx_df.sort_values("date", ascending=False).to_json(orient="records")

    @staticmethod
    def get_info():
        return {
            "type": "function",
            "function": {
                "name": "get_transactions",
                "description": "Return ledger entries for an account; optional ISO-date range filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string"},
                        "date_from": {
                            "type": "string",
                            "description": "Optional lower bound YYYY-MM-DD",
                        },
                        "date_to": {
                            "type": "string",
                            "description": "Optional upper bound YYYY-MM-DD",
                        },
                    },
                    "required": ["account_id"],
                },
            },
        }


get_transactions_schema = GetTransactions.get_info()
get_transactions = StructuredTool.from_function(
    func=GetTransactions.invoke,
    name=get_transactions_schema["function"]["name"],
    description=get_transactions_schema["function"]["description"],
)
