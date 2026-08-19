from .base_agent import BaseAgent


class FollowUpAgent(BaseAgent):
    name = "followup_agent"
    system_prompt = (
        "You are Astra's Follow-Up Agent. You re-engage leads who went quiet, "
        "using a warm, no-pressure tone (this is part of a 10-day follow-up "
        "sequence). Reference their original interest if known, and give them "
        "an easy way to re-engage. Keep it under 3 sentences."
    )

    def handle(self, message: str, context: dict) -> dict:
        reply = self._call_llm(message, extra_system=f"Niche: {context.get('niche', 'general')}")
        return {
            "reply": reply,
            "lead_captured": True,
            "next_action": None,
        }
