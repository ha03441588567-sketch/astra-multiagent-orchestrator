from .base_agent import BaseAgent


class LeadQualifierAgent(BaseAgent):
    name = "lead_qualifier_agent"
    system_prompt = (
        "You are Astra's Lead Qualifier. Your job is to ask 1-2 sharp follow-up "
        "questions to understand urgency and budget (e.g. timeline, property type, "
        "problem severity) so the sales team knows if this is a hot lead. "
        "Keep it short and conversational, never sound like a form."
    )

    def handle(self, message: str, context: dict) -> dict:
        reply = self._call_llm(message, extra_system=f"Niche: {context.get('niche', 'general')}")
        return {
            "reply": reply,
            "lead_captured": True,
            "next_action": "route_to_scheduler",
        }
