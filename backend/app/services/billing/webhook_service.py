from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.billing import Subscription, Payment, BillingEvent, ProcessedWebhook
from app.models import User
from app.services.billing.provider_factory import get_provider
from app.services.billing.schemas import PLANS, CREDIT_PACKS
import uuid
import logging

logger = logging.getLogger(__name__)

async def process_webhook(provider_name: str, payload: bytes, signature: str, db: AsyncSession):
    provider = get_provider(provider_name)
    
    try:
        event = provider.verify_webhook(payload, signature)
    except Exception as e:
        logger.error(f"Webhook verification failed: {e}")
        raise ValueError(f"Webhook verification failed: {e}")

    # Idempotency check
    if event.event_id:
        existing = await db.execute(select(ProcessedWebhook).filter(ProcessedWebhook.id == event.event_id))
        if existing.scalars().first():
            logger.info(f"Webhook {event.event_id} already processed")
            return {"status": "already_processed"}
            
    # Process "paid" events
    if event.status == "paid" and event.user_id:
        user_res = await db.execute(select(User).filter(User.id == event.user_id))
        user = user_res.scalars().first()
        
        if user:
            credits_to_add = 0
            if event.plan and event.plan in PLANS:
                credits_to_add = PLANS[event.plan]["credits"]
                # Update user subscription
                user.plan = event.plan
                
                # Record subscription
                sub = Subscription(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    plan=event.plan,
                    provider=provider_name,
                    status="active"
                )
                db.add(sub)
                
            elif event.pack and event.pack in CREDIT_PACKS:
                credits_to_add = CREDIT_PACKS[event.pack]["credits"]
                
            user.credits += credits_to_add
            
            # Record payment
            payment = Payment(
                id=str(uuid.uuid4()),
                user_id=user.id,
                provider=provider_name,
                provider_payment_id=event.event_id,
                amount=event.amount,
                currency=event.currency,
                credits_added=credits_to_add,
                status="succeeded"
            )
            db.add(payment)
            
            # Audit log
            billing_event = BillingEvent(
                id=str(uuid.uuid4()),
                user_id=user.id,
                event_type=f"{provider_name}.paid",
                provider=provider_name,
                payload=event.raw_payload
            )
            db.add(billing_event)

    # Mark as processed
    if event.event_id:
        processed = ProcessedWebhook(id=event.event_id, provider=provider_name)
        db.add(processed)

    await db.commit()
    return {"status": "success"}
