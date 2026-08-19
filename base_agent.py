"""
Astra AI Workforce Platform — Base Agent
All specialized agents (Receptionist, Lead Qualifier, Scheduler, Follow-up)
inherit from this class so the Orchestrator can call them uniformly.
"""

from abc import ABC, abstractmethod
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class BaseAgent(ABC):
    name: str = "base_agent"
    system_prompt: str = "You are a helpful AI assistant."
    model: str = "claude-sonnet-4-6"

    @abstractmethod
    def handle(self, message: str, context: dict) -> dict:
        """
        Process an incoming message and return a dict:
        {
            "reply": str,
            "lead_captured": bool,
            "next_action": str | None
        }
        """
        raise NotImplementedError

    def _call_llm(self, user_message: str, extra_system: str = "") -> str:
        """Shared helper so every agent talks to Claude the same way."""
        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=500,
                system=f"{self.system_prompt}\n{extra_system}",
                messages=[{"role": "user", "content": user_message}],
            )
            return "".join(
                block.text for block in response.content if block.type == "text"
            ).strip()
        except Exception as e:
            # Graceful fallback so a missing/invalid API key never crashes the demo
            return (
                f"[{self.name} fallback reply — LLM unavailable: {e}] "
                f"Thanks for reaching out, someone from our team will follow up shortly."
            )
