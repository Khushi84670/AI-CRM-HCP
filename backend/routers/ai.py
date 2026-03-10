from fastapi import APIRouter

from models.schemas import AIInteractionRequest, AIToolResult
from langgraph_agent.graph import run_agent


router = APIRouter()


@router.post("/ai/chat", response_model=AIToolResult)
def ai_chat(request: AIInteractionRequest) -> AIToolResult:
    """
    Entry point for the conversational AI assistant.

    The LangGraph agent will:
    - Detect intent
    - Select the appropriate tool
    - Execute it
    - Return a structured result
    """
    result = run_agent(request.input_text)

    interaction = result.get("interaction")
    followups = result.get("suggestions") or result.get("followup_suggestions")

    return AIToolResult(
        message=result.get("message", "OK"),
        interaction=interaction,
        followup_suggestions=followups,
    )

