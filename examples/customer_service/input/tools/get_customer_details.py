import json
from typing import Any, Dict

from langchain.tools import StructuredTool
from util import get_dict_json


class GetCustomerDetails:
    @staticmethod
    def invoke(data: Dict[str, Any], customer_id: str) -> str:
        customers = get_dict_json(data["customers"], "customer_id")
        if customer_id in customers:
            return json.dumps(customers[customer_id])
        return "Error: customer not found"

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_customer_details",
                "description": "Return the master-data/KYC profile of a customer.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Bank-internal customer identifier, e.g. 'CUS1001'.",
                        }
                    },
                    "required": ["customer_id"],
                },
            },
        }


get_customer_details_schema = GetCustomerDetails.get_info()
get_customer_details = StructuredTool.from_function(
    func=GetCustomerDetails.invoke,
    name=get_customer_details_schema["function"]["name"],
    description=get_customer_details_schema["function"]["description"],
)
