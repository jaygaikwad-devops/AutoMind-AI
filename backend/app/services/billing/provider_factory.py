from app.services.billing.providers.base import BaseBillingProvider
from app.services.billing.providers.stripe_provider import StripeProvider
from app.services.billing.providers.razorpay_provider import RazorpayProvider

def get_provider(provider_name: str) -> BaseBillingProvider:
    if provider_name.lower() == "stripe":
        return StripeProvider()
    elif provider_name.lower() == "razorpay":
        return RazorpayProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
