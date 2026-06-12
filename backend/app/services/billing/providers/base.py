from abc import ABC, abstractmethod
from typing import Dict, Any
from app.services.billing.schemas import NormalizedWebhookEvent

class BaseBillingProvider(ABC):
    @abstractmethod
    def create_checkout(self, user_id: str, item_id: str, item_type: str, currency: str) -> str:
        """
        item_type: 'plan' or 'pack'
        item_id: e.g. 'growth' or 'pack_500'
        currency: 'usd' or 'inr'
        Returns the checkout session URL or order ID.
        """
        pass

    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> NormalizedWebhookEvent:
        """
        Verifies the webhook signature and normalizes the event.
        Raises an exception if verification fails.
        """
        pass
