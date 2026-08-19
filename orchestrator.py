"""
Astra AI Workforce Platform — Orchestrator
This is the "router agent": it classifies intent, decides which specialized
agent should handle the message, calls that agent, and logs everything.
"""

import os
import uuid
import json
from anthropic import Anthropic

from agents import ReceptionistAgent, LeadQualifierAgent, SchedulerAgent, FollowUpAgent
import database as db

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

AGENT_REGISTRY = {
    "receptionist_agent": ReceptionistAgent(),
    "lead_qualifier_agent": LeadQualifierAgent(),
    "scheduler_agent": SchedulerAgent(),
    "followup_agent": FollowUpAgent(),
}

INTENT_TO_AGENT = {
    "new_lead": "receptionist_agent",
    "general_inquiry": "receptionist_agent",
    "pricing_question": "lead_qualifier_agent",
    "booking_request": "scheduler_agent",
    "follow_up_needed": "followup_agent",
    "complaint": "receptionist_agent",
}

VALID_INTENTS = list(INTENT_TO_AGENT.keys())


def classify_intent(message: str) -> str:
    """Ask Claude to classify the incoming message into one of our known intents."""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=20,
            system=(
                "Classify the customer message into EXACTLY one of these labels: "
                f"{', '.join(VALID_INTENTS)}. "
                "Respond with ONLY the label, nothing else."
            ),
            messages=[{"role": "user", "content": message}],
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip().lower()
        for intent in VALID_INTENTS:
            if intent in text:
                return intent
        return "general_inquiry"
    except Exception:
        # Simple keyword fallback if the LLM call fails (e.g. no API key set)
        lower = message.lower()
        if any(w in lower for w in ["book", "schedule", "appointment", "available"]):
            return "booking_request"
        if any(w in lower for w in ["price", "cost", "how much", "quote"]):
            return "pricing_question"
        if any(w in lower for w in ["angry", "refund", "complaint", "unhappy"]):
            return "complaint"
        return "general_inquiry"


def run_orchestrator(payload: dict) -> dict:
    """
    Main entry point. Takes an IncomingMessage-shaped dict, routes it to the
    right agent, logs the conversation + lead, and returns the response.
    """
    conversation_id = payload.get("conversation_id") or str(uuid.uuid4())
    business_id = payload["business_id"]
    niche = payload.get("niche", "general")
    channel = payload.get("channel", "web_chat")
    message = payload["message"]

    # 1. log the inbound customer message
    db.log_message(conversation_id, business_id, niche, channel, "customer", None, message)

    # 2. classify intent
    intent = classify_intent(message)

    # 3. route to the right specialized agent
    agent_name = INTENT_TO_AGENT.get(intent, "receptionist_agent")
    agent = AGENT_REGISTRY[agent_name]

    context = {
        "niche": niche,
        "customer_name": payload.get("customer_name"),
        "customer_phone": payload.get("customer_phone"),
        "customer_email": payload.get("customer_email"),
    }
    result = agent.handle(message, context)

    # 4. log the agent's reply
    db.log_message(conversation_id, business_id, niche, channel, "agent", agent_name,
                    result["reply"], intent)

    # 5. capture lead + create follow-up task if relevant
    if result.get("lead_captured"):
        db.create_lead(
            business_id, niche,
            name=payload.get("customer_name"),
            phone=payload.get("customer_phone"),
            email=payload.get("customer_email"),
            notes=f"Captured via {agent_name} | intent={intent}",
        )

    if result.get("next_action"):
        db.create_task(business_id, agent_name, result["next_action"])

    return {
        "conversation_id": conversation_id,
        "routed_to_agent": agent_name,
        "intent": intent,
        "reply": result["reply"],
        "lead_captured": result.get("lead_captured", False),
        "next_action": result.get("next_action"),
    }
