import json
from typing import Any, Dict

import pandas as pd
from langchain.tools import StructuredTool
from util import get_dict_json


class GetLoanDetails:
    @staticmethod
    def invoke(data: Dict[str, Any], loan_id: str) -> str:
        loans = get_dict_json(data["loans"], "loan_id")
        if loan_id not in loans:
            return "Error: loan not found"
        loan = loans[loan_id]
        # attach most recent payments
        pay_df: pd.DataFrame = data["loan_payments"]
        payments = (
            pay_df[pay_df["loan_id"] == loan_id]
            .sort_values("date", ascending=False)
            .head(12)
        )
        loan["recent_payments"] = json.loads(payments.to_json(orient="records"))
        return json.dumps(loan)

    @staticmethod
    def get_info():
        return {
            "type": "function",
            "function": {
                "name": "get_loan_details",
                "description": "Return amortising loan metadata and recent payments.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "loan_id": {"type": "string"},
                    },
                    "required": ["loan_id"],
                },
            },
        }


get_loan_details_schema = GetLoanDetails.get_info()
get_loan_details = StructuredTool.from_function(
    func=GetLoanDetails.invoke,
    name=get_loan_details_schema["function"]["name"],
    description=get_loan_details_schema["function"]["description"],
)
