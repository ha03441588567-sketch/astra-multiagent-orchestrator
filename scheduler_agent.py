from .base_agent import BaseAgent


class SchedulerAgent(BaseAgent):
    name = "scheduler_agent"
    system_prompt = (
        "You are Astra's Scheduling Assistant. You help customers pick a time for "
        "an appointment, inspection, or consultation. Suggest 2-3 concrete time "
        "windows (e.g. 'tomorrow 10am-12pm' or 'Thursday afternoon') and confirm "
        "clearly. Keep it brief and action-oriented."
    )

    def handle(self, message: str, context: dict) -> dict:
        reply = self._call_llm(message, extra_system=f"Niche: {context.get('niche', 'general')}")
        return {
            "reply": reply,
            "lead_captured": True,
            "next_action": "schedule_followup_reminder",
        }
