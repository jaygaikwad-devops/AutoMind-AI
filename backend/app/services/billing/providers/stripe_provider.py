import stripe
from app.core.config import settings
from app.services.billing.providers.base import BaseBillingProvider
from app.services.billing.schemas import NormalizedWebhookEvent, PLANS, CREDIT_PACKS

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeProvider(BaseBillingProvider):
    def create_checkout(self, user_id: str, item_id: str, item_type: str, currency: str) -> str:
        catalog = PLANS if item_type == "plan" else CREDIT_PACKS
        if item_id not in catalog:
            raise ValueError(f"Invalid {item_type}: {item_id}")

        item_data = catalog[item_id]
        amount = item_data[f"price_{currency.lower()}"]

        # Convert to cents
        amount_cents = int(amount * 100)
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': f"AutoMind {item_id.capitalize()}",
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url="http://localhost:3000/dashboard?payment=success",
            cancel_url="http://localhost:3000/pricing",
            metadata={
                "user_id": user_id,
                "item_id": item_id,
                "item_type": item_type,
            }
        )
        return session.url

    def verify_webhook(self, payload: bytes, signature: str) -> NormalizedWebhookEvent:
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise Exception(f"Invalid payload: {e}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid signature: {e}")

        # Normalize
        if event.type == 'checkout.session.completed':
            session = event.data.object
            metadata = session.get("metadata", {})
            user_id = metadata.get("user_id")
            item_id = metadata.get("item_id")
            item_type = metadata.get("item_type")

            amount = session.amount_total / 100.0 if session.amount_total else 0.0
            currency = session.currency or "usd"
            
            plan = item_id if item_type == "plan" else None
            pack = item_id if item_type == "pack" else None

            return NormalizedWebhookEvent(
                provider="stripe",
                event_id=event.id,
                user_id=user_id,
                plan=plan,
                pack=pack,
                amount=amount,
                currency=currency,
                status="paid",
                raw_payload=event.to_dict()
            )
        
        # Unhandled event
        return NormalizedWebhookEvent(
            provider="stripe",
            event_id=event.id,
            amount=0,
            currency="usd",
            status="ignored",
            raw_payload=event.to_dict()
        )
