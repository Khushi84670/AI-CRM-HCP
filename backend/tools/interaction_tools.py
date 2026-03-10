from datetime import date, time
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from models.database import SessionLocal
from models.schemas import (
    InteractionCreate,
    InteractionRead,
    InteractionUpdate,
)
from services import db_service
from services.groq_client import GroqClient


def _get_db() -> Session:
    return SessionLocal()


def _interaction_to_read(interaction) -> InteractionRead:
    return InteractionRead(
        id=interaction.id,
        hcp_id=interaction.hcp_id,
        hcp_name=interaction.hcp.name,
        interaction_type=interaction.interaction_type,
        date=interaction.date,
        time=interaction.time,
        attendees=interaction.attendees,
        topics=interaction.topics,
        materials_shared=interaction.materials_shared,
        samples_distributed=interaction.samples_distributed,
        sentiment=interaction.sentiment,
        outcomes=interaction.outcomes,
        followup_actions=interaction.followup_actions,
        summary=interaction.summary,
    )


@tool("log_interaction")
def log_interaction_tool(input_text: str, interaction_date: Optional[date] = None, interaction_time: Optional[time] = None) -> Dict[str, Any]:
    """Log a new HCP interaction from free-text notes."""
    db = _get_db()
    client = GroqClient()

    entities = client.extract_entities(input_text)
    summary = client.summarize_text(input_text)

    interaction_in = InteractionCreate(
        hcp_name=entities.get("hcp_name") or "Unknown HCP",
        interaction_type=entities.get("interaction_type") or "Meeting",
        date=interaction_date or date.today(),
        time=interaction_time or time(9, 0),
        attendees=entities.get("attendees"),
        topics=entities.get("topics"),
        materials_shared=entities.get("materials_shared"),
        samples_distributed=entities.get("samples_distributed"),
        sentiment=entities.get("sentiment"),
        outcomes=entities.get("outcomes"),
        followup_actions=entities.get("followup_actions"),
        summary=summary,
    )

    interaction = db_service.create_interaction(db, interaction_in)
    db.close()
    return {
        "message": "Interaction logged successfully.",
        "interaction": _interaction_to_read(interaction).dict(),
    }


@tool("edit_interaction")
def edit_interaction_tool(interaction_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Edit an existing HCP interaction given its ID and partial field updates."""
    db = _get_db()
    interaction_update = InteractionUpdate(**updates)
    interaction = db_service.update_interaction(db, interaction_id, interaction_update)
    db.close()
    if not interaction:
        return {"message": f"Interaction {interaction_id} not found.", "interaction": None}
    return {
        "message": "Interaction updated successfully.",
        "interaction": _interaction_to_read(interaction).dict(),
    }


@tool("summarize_interaction")
def summarize_interaction_tool(text: str) -> Dict[str, Any]:
    """Summarize meeting notes into a concise CRM summary."""
    client = GroqClient()
    summary = client.summarize_text(text)
    return {"message": "Summary generated.", "summary": summary}


@tool("suggest_followup")
def suggest_followup_tool(text: str) -> Dict[str, Any]:
    """Suggest follow-up actions based on interaction notes."""
    client = GroqClient()
    suggestions = client.suggest_followups(text)
    return {"message": "Follow-up suggestions generated.", "suggestions": suggestions}


@tool("retrieve_interaction_history")
def retrieve_interaction_history_tool(hcp_name: str) -> Dict[str, Any]:
    """Retrieve previous interactions with a specific HCP."""
    db = _get_db()
    interactions = db_service.get_hcp_history(db, hcp_name)
    db.close()
    return {
        "message": f"Retrieved {len(interactions)} interactions for {hcp_name}.",
        "interactions": [
            _interaction_to_read(interaction).dict() for interaction in interactions
        ],
    }

