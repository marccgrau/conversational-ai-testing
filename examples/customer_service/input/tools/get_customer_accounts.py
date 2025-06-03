from typing import Any, Dict

import pandas as pd
from langchain.tools import StructuredTool


class GetCustomerAccounts:
    @staticmethod
    def invoke(data: Dict[str, Any], customer_id: str) -> str:
        accounts_df: pd.DataFrame = data["accounts"]
        accounts = accounts_df[accounts_df["customer_id"] == customer_id]
        if accounts.empty:
            return "Error: no accounts found for customer"
        return accounts.to_json(orient="records")

    @staticmethod
    def get_info():
        return {
            "type": "function",
            "function": {
                "name": "get_customer_accounts",
                "description": "Return all deposit accounts (current, savings, etc.) held by a specific customer.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "e.g. 'CUS1001'",
                        }
                    },
                    "required": ["customer_id"],
                },
            },
        }


get_customer_accounts_schema = GetCustomerAccounts.get_info()
get_customer_accounts = StructuredTool.from_function(
    func=GetCustomerAccounts.invoke,
    name=get_customer_accounts_schema["function"]["name"],
    description=get_customer_accounts_schema["function"]["description"],
)
