from app.services.billing.provider_factory import get_provider

def create_checkout(user_id: str, item_id: str, item_type: str, provider_name: str, currency: str) -> str:
    """
    Creates a checkout session for a plan or a pack via the selected provider.
    Returns the session URL or order ID for the frontend.
    """
    provider = get_provider(provider_name)
    return provider.create_checkout(user_id, item_id, item_type, currency)
