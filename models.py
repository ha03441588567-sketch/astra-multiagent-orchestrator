"""
Astra AI Workforce Platform — Data Models
Pydantic schemas used across the orchestrator and agents.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


NicheType = Literal["roofing", "dental", "real_estate", "solar", "general"]
IntentType = Literal[
    "new_lead", "booking_request", "general_inquiry",
    "follow_up_needed", "complaint", "pricing_question"
]


class IncomingMessage(BaseModel):
    """A single inbound message from a customer (chat, SMS, or voice transcript)."""
    business_id: str = Field(..., description="Unique ID of the client business using Astra")
    niche: NicheType = "general"
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    channel: Literal["web_chat", "sms", "voice", "whatsapp"] = "web_chat"
    message: str


class OrchestratorResponse(BaseModel):
    """What the orchestrator sends back after routing + running an agent."""
    conversation_id: str
    routed_to_agent: str
    intent: IntentType
    reply: str
    lead_captured: bool = False
    next_action: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Lead(BaseModel):
    id: Optional[int] = None
    business_id: str
    niche: NicheType
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    status: Literal["new", "qualified", "scheduled", "followed_up", "closed"] = "new"
    notes: Optional[str] = None
    created_at: Optional[str] = None


class Task(BaseModel):
    id: Optional[int] = None
    business_id: str
    agent_name: str
    description: str
    status: Literal["pending", "in_progress", "done"] = "pending"
    created_at: Optional[str] = None
