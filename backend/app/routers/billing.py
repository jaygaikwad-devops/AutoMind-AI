from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.services.billing.billing_service import create_checkout
from app.services.billing.webhook_service import process_webhook
from app.models.billing import Subscription, Payment
from app.core.config import settings
from sqlalchemy import select

router = APIRouter()

class CheckoutRequest(BaseModel):
    item_id: str
    item_type: str # 'plan' or 'pack'
    provider: str # 'stripe' or 'razorpay'
    currency: str # 'usd' or 'inr'

@router.post("/checkout")
async def start_checkout(
    body: CheckoutRequest, 
    current_user: User = Depends(get_current_user)
):
    try:
        url_or_id = create_checkout(
            user_id=current_user.id,
            item_id=body.item_id,
            item_type=body.item_type,
            provider_name=body.provider,
            currency=body.currency
        )
        return {"ok": True, "url_or_id": url_or_id, "provider": body.provider}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing signature")
        
    try:
        await process_webhook("stripe", payload, sig_header, db)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("x-razorpay-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing signature")
        
    try:
        await process_webhook("razorpay", payload, sig_header, db)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/config")
async def get_billing_config():
    return {
        "razorpay_key_id": settings.RAZORPAY_KEY_ID
    }

@router.get("/status")
async def get_billing_status(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Subscription)
        .filter(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
    )
    sub = result.scalars().first()
    
    # Calculate total credits based on plan
    from app.services.billing.schemas import PLANS
    plan_name = current_user.plan or "starter"
    credits_total = PLANS.get(plan_name, {}).get("credits", 0)

    return {
        "plan": plan_name,
        "credits_remaining": current_user.credits,
        "credits_total": credits_total,
        "renewal_date": sub.renewal_date if sub else None,
        "provider": sub.provider if sub else None,
        "subscription_status": sub.status if sub else "active"
    }

@router.get("/history")
async def get_billing_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()
    
    # Format payment history with type
    history = []
    for p in payments:
        # Determine type based on amount or logic (simplified for now)
        p_type = "Credit Pack" if "pack" in (p.provider_payment_id or "") else "Plan Upgrade"
        
        history.append({
            "id": p.id,
            "date": p.created_at,
            "type": p_type,
            "credits": p.credits_added,
            "amount": p.amount,
            "currency": p.currency,
            "status": p.status
        })
        
    return history

