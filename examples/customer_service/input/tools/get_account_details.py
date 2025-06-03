import json
from typing import Any, Dict

from langchain.tools import StructuredTool
from util import get_dict_json


class GetAccountDetails:
    @staticmethod
    def invoke(data: Dict[str, Any], account_id: str) -> str:
        accounts = get_dict_json(data["accounts"], "account_id")
        if account_id in accounts:
            return json.dumps(accounts[account_id])
        return "Error: account not found"

    @staticmethod
    def get_info():
        return {
            "type": "function",
            "function": {
                "name": "get_account_details",
                "description": "Fetch full details of a single deposit account.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "account_id": {
                            "type": "string",
                            "description": "e.g. 'ACC2001'",
                        }
                    },
                    "required": ["account_id"],
                },
            },
        }


get_account_details_schema = GetAccountDetails.get_info()
get_account_details = StructuredTool.from_function(
    func=GetAccountDetails.invoke,
    name=get_account_details_schema["function"]["name"],
    description=get_account_details_schema["function"]["description"],
)
