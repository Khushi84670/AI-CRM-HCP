import os
from typing import List, Literal, Optional

from groq import Groq


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PRIMARY_MODEL = os.getenv("GROQ_PRIMARY_MODEL", "gemma2-9b-it")
FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "llama-3.3-70b-versatile")


class GroqClient:
    def __init__(self) -> None:
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set")
        self.client = Groq(api_key=GROQ_API_KEY)

    def _chat_completion(
        self,
        messages: List[dict],
        model_preference: Literal["primary", "fallback"] = "primary",
        temperature: float = 0.2,
    ) -> str:
        model = PRIMARY_MODEL if model_preference == "primary" else FALLBACK_MODEL
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def summarize_text(self, text: str) -> str:
        prompt = (
            "You are an assistant for pharmaceutical field reps. "
            "Summarize the following HCP interaction in 2-3 concise sentences, "
            "focusing on key topics, sentiment, and outcomes.\n\n"
            f"Interaction notes:\n{text}"
        )
        return self._chat_completion(
            [
                {"role": "system", "content": "You are a helpful CRM summarization assistant."},
                {"role": "user", "content": prompt},
            ]
        )

    def extract_entities(self, text: str) -> dict:
        prompt = (
            "You are extracting structured CRM fields from free-text notes about "
            "pharmaceutical field interactions with healthcare professionals (HCPs).\n"
            "Return a JSON object with the following keys:\n"
            "hcp_name, interaction_type, attendees, topics, materials_shared, "
            "samples_distributed, sentiment, outcomes, followup_actions.\n"
            "Use null if a field is not mentioned. Sentiment must be one of: "
            "Positive, Neutral, Negative.\n"
            "Text:\n"
            f"{text}"
        )
        content = self._chat_completion(
            [
                {"role": "system", "content": "You are an information extraction assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        # Very lightweight safety parsing: Groq models are instructed to return JSON only.
        import json

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    def suggest_followups(self, text: str) -> List[str]:
        prompt = (
            "Based on the following HCP interaction notes, suggest 3 concrete follow-up "
            "actions for a pharmaceutical sales representative. "
            "Return them as a numbered list.\n\n"
            f"{text}"
        )
        content = self._chat_completion(
            [
                {"role": "system", "content": "You are a follow-up planning assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        suggestions = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped[0].isdigit() and "." in stripped:
                stripped = stripped.split(".", 1)[1].strip()
            suggestions.append(stripped)
        return suggestions

