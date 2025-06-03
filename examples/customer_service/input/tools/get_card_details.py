import json
from typing import Any, Dict

from langchain.tools import StructuredTool
from util import get_dict_json


class GetCardDetails:
    @staticmethod
    def invoke(data: Dict[str, Any], card_id: str) -> str:
        cards = get_dict_json(data["cards"], "card_id")
        if card_id in cards:
            return json.dumps(cards[card_id])
        return "Error: card not found"

    @staticmethod
    def get_info():
        return {
            "type": "function",
            "function": {
                "name": "get_card_details",
                "description": "Return debit/credit-card metadata including status and limits.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "card_id": {"type": "string", "description": "e.g. 'CARD3002'"},
                    },
                    "required": ["card_id"],
                },
            },
        }


get_card_details_schema = GetCardDetails.get_info()
get_card_details = StructuredTool.from_function(
    func=GetCardDetails.invoke,
    name=get_card_details_schema["function"]["name"],
    description=get_card_details_schema["function"]["description"],
)
