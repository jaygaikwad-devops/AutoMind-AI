from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, JSON
from datetime import datetime
from . import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan = Column(String, index=True)
    provider = Column(String, index=True)
    provider_subscription_id = Column(String, index=True, nullable=True)
    status = Column(String) # active, past_due, canceled, trailing
    renewal_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider = Column(String, index=True)
    provider_payment_id = Column(String, index=True, nullable=True)
    amount = Column(Float)
    currency = Column(String, default="usd")
    credits_added = Column(Integer, default=0)
    status = Column(String) # succeeded, failed, pending
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class BillingEvent(Base):
    __tablename__ = "billing_events"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    event_type = Column(String) # e.g. checkout.session.completed
    provider = Column(String)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class ProcessedWebhook(Base):
    __tablename__ = "processed_webhooks"

    id = Column(String, primary_key=True, index=True) # Usually the provider's event ID
    provider = Column(String, index=True)
    processed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
