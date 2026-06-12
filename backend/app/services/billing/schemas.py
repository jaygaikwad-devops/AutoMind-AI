from pydantic import BaseModel
from typing import Optional, Dict, Any

PLANS = {
    "starter": {
        "credits": 500,
        "price_inr": 4999,
        "price_usd": 59
    },
    "growth": {
        "credits": 2000,
        "price_inr": 9999,
        "price_usd": 119
    },
    "agency": {
        "credits": 5000,
        "price_inr": 14999,
        "price_usd": 199
    }
}

CREDIT_PACKS = {
    "pack_500": {
        "credits": 500,
        "price_inr": 999,
        "price_usd": 12
    },
    "pack_1000": {
        "credits": 1000,
        "price_inr": 1799,
        "price_usd": 22
    },
    "pack_5000": {
        "credits": 5000,
        "price_inr": 6999,
        "price_usd": 85
    }
}

class NormalizedWebhookEvent(BaseModel):
    provider: str
    event_id: str
    user_id: Optional[str] = None
    plan: Optional[str] = None
    pack: Optional[str] = None
    amount: float
    currency: str
    status: str
    raw_payload: Dict[str, Any]
