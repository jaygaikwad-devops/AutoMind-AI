from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User

class CreditReservationError(Exception):
    pass

class CreditService:
    @staticmethod
    async def reserve_credits(db: AsyncSession, user_id: str, amount: int, job_id: str) -> bool:
        """
        Reserves credits for a job.
        Raises CreditReservationError if the user does not have enough unreserved credits.
        """
        result = await db.execute(select(User).filter(User.id == user_id).with_for_update())
        user = result.scalars().first()
        
        if not user:
            raise CreditReservationError("User not found.")
            
        unreserved_credits = user.credits - (user.credits_reserved or 0)
        
        if unreserved_credits < amount:
            raise CreditReservationError(f"Insufficient credits. Requires {amount}, but only has {unreserved_credits} available.")
            
        # Add to reserved
        user.credits_reserved = (user.credits_reserved or 0) + amount
        await db.commit()
        return True

    @staticmethod
    async def commit_credits(db: AsyncSession, user_id: str, amount: int) -> bool:
        """
        Called when a job completes successfully.
        Deducts the amount from BOTH the actual credits and the reserved credits pool.
        """
        result = await db.execute(select(User).filter(User.id == user_id).with_for_update())
        user = result.scalars().first()
        
        if user:
            user.credits = max(0, user.credits - amount)
            user.credits_reserved = max(0, (user.credits_reserved or 0) - amount)
            await db.commit()
            return True
        return False

    @staticmethod
    async def refund_credits(db: AsyncSession, user_id: str, amount: int) -> bool:
        """
        Called when a job fails.
        Releases the reserved amount back to the available pool.
        """
        result = await db.execute(select(User).filter(User.id == user_id).with_for_update())
        user = result.scalars().first()
        
        if user:
            user.credits_reserved = max(0, (user.credits_reserved or 0) - amount)
            await db.commit()
            return True
        return False

    @staticmethod
    def commit_credits_sync(db, user_id: str, amount: int) -> bool:
        """Synchronous version for Celery workers"""
        user = db.query(User).filter(User.id == user_id).with_for_update().first()
        if user:
            user.credits = max(0, user.credits - amount)
            user.credits_reserved = max(0, (user.credits_reserved or 0) - amount)
            db.commit()
            return True
        return False

    @staticmethod
    def refund_credits_sync(db, user_id: str, amount: int) -> bool:
        """Synchronous version for Celery workers"""
        user = db.query(User).filter(User.id == user_id).with_for_update().first()
        if user:
            user.credits_reserved = max(0, (user.credits_reserved or 0) - amount)
            db.commit()
            return True
        return False
