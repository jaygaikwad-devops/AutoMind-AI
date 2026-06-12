import razorpay
import hmac
import hashlib
import json
from app.core.config import settings
from app.services.billing.providers.base import BaseBillingProvider
from app.services.billing.schemas import NormalizedWebhookEvent, PLANS, CREDIT_PACKS

# Handle potential missing keys gracefully
client = None
if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class RazorpayProvider(BaseBillingProvider):
    def create_checkout(self, user_id: str, item_id: str, item_type: str, currency: str) -> str:
        if not client:
            raise Exception("Razorpay not configured")
            
        catalog = PLANS if item_type == "plan" else CREDIT_PACKS
        if item_id not in catalog:
            raise ValueError(f"Invalid {item_type}: {item_id}")

        item_data = catalog[item_id]
        amount = item_data[f"price_{currency.lower()}"]

        # Convert to paise (cents)
        amount_paise = int(amount * 100)
        
        # Razorpay creates an order, not a direct checkout session URL.
        # The frontend needs this order_id to initialize the Razorpay popup.
        data = {
            "amount": amount_paise,
            "currency": currency.upper(),
            "receipt": f"rcpt_{user_id}_{item_id}"[:40], # Razorpay limits receipt to 40 chars
            "notes": {
                "user_id": user_id,
                "item_id": item_id,
                "item_type": item_type
            }
        }
        
        order = client.order.create(data=data)
        return order['id']

    def verify_webhook(self, payload: bytes, signature: str) -> NormalizedWebhookEvent:
        if not settings.RAZORPAY_WEBHOOK_SECRET:
            raise Exception("Razorpay webhook secret not configured")
            
        # Verify signature
        expected_signature = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, signature):
            raise Exception("Invalid signature")
            
        data = json.loads(payload.decode('utf-8'))
        event_name = data.get('event')
        
        if event_name == 'payment.captured':
            payment_entity = data['payload']['payment']['entity']
            notes = payment_entity.get('notes', {})
            
            user_id = notes.get('user_id')
            item_id = notes.get('item_id')
            item_type = notes.get('item_type')
            
            amount = payment_entity.get('amount', 0) / 100.0
            currency = payment_entity.get('currency', 'INR')
            
            plan = item_id if item_type == "plan" else None
            pack = item_id if item_type == "pack" else None
            
            # The event id could be the payment id or webhook event id
            event_id = data.get('id', '') # Webhook event ID
            
            return NormalizedWebhookEvent(
                provider="razorpay",
                event_id=event_id,
                user_id=user_id,
                plan=plan,
                pack=pack,
                amount=amount,
                currency=currency,
                status="paid",
                raw_payload=data
            )
            
        return NormalizedWebhookEvent(
            provider="razorpay",
            event_id=data.get('id', ''),
            amount=0,
            currency="inr",
            status="ignored",
            raw_payload=data
        )
