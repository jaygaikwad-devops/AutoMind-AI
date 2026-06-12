from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from datetime import datetime

# Pricing structure in Marketing Credits
ACTION_COSTS = {
    "caption_generation": 1,
    "hashtag_generation": 1,
    "hook_generation": 2,
    "blog_generation": 10,
    "ad_campaign_generation": 20,
    "video_script": 5,
    "reel_generation": 50,
    "standard_video": 50,
    "premium_video": 200,
}

# Subscriptions map
PLAN_CREDITS = {
    "starter": 500,
    "growth": 2000,
    "agency": 5000,
}

async def consume_credits(db: AsyncSession, user_id: str, action_type: str) -> bool:
    """
    Deducts credits for a given action type. 
    Raises 402 Payment Required if insufficient credits.
    """
    if action_type not in ACTION_COSTS:
        raise ValueError(f"Unknown action_type: {action_type}")
        
    cost = ACTION_COSTS[action_type]
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    if user.credits < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, 
            detail=f"Insufficient Marketing Credits. Action requires {cost} credits, but you only have {user.credits}."
        )
        
    user.credits -= cost
    db.add(user)
    await db.commit()
    
    return True
