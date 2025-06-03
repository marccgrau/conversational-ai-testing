import json
from typing import Any, Dict

import pandas as pd
from langchain.tools import StructuredTool


class UpdateCardStatus:
    @staticmethod
    def invoke(data: Dict[str, Any], card_id: str, new_status: str) -> str:
        if new_status not in ["active", "locked"]:
            return "Error: new_status must be 'active' or 'locked'"
        cards_df: pd.DataFrame = data["cards"]
        idx = cards_df.index[cards_df["card_id"] == card_id].tolist()
        if not idx:
            return "Error: card not found"
        cards_df.at[idx[0], "status"] = new_status
        return json.dumps(cards_df.loc[idx[0]].to_dict())

    @staticmethod
    def get_info():
        return {
            "type": "function",
            "function": {
                "name": "update_card_status",
                "description": "Lock (freeze) or unlock a card.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "card_id": {"type": "string"},
                        "new_status": {
                            "type": "string",
                            "enum": ["active", "locked"],
                        },
                    },
                    "required": ["card_id", "new_status"],
                },
            },
        }


update_card_status_schema = UpdateCardStatus.get_info()
update_card_status = StructuredTool.from_function(
    func=UpdateCardStatus.invoke,
    name=update_card_status_schema["function"]["name"],
    description=update_card_status_schema["function"]["description"],
)
