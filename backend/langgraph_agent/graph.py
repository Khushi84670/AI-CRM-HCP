from typing import Any, Dict, Literal, Optional, TypedDict

from langgraph.graph import END, StateGraph

from services.groq_client import GroqClient
from tools.interaction_tools import (
    log_interaction_tool,
    edit_interaction_tool,
    summarize_interaction_tool,
    suggest_followup_tool,
    retrieve_interaction_history_tool,
)


class AgentState(TypedDict, total=False):
    """State passed through the LangGraph agent."""

    input_text: str
    intent: Optional[str]
    tool_name: Optional[str]
    tool_args: Dict[str, Any]
    result: Dict[str, Any]


TOOLS_MAP = {
    "log_interaction": log_interaction_tool,
    "edit_interaction": edit_interaction_tool,
    "summarize_interaction": summarize_interaction_tool,
    "suggest_followup": suggest_followup_tool,
    "retrieve_interaction_history": retrieve_interaction_history_tool,
}


def _detect_intent(state: AgentState) -> AgentState:
    """Use Groq LLM to detect intent and determine which tool to call."""
    client = GroqClient()
    text = state["input_text"]
    prompt = (
        "You are an AI router for an HCP interaction logging system.\n"
        "Given the user's message, choose the most appropriate tool and arguments.\n"
        "Available tools and expected arguments:\n"
        "1. log_interaction: {{\"tool\": \"log_interaction\", \"tool_args\": {\"input_text\": str}}}\n"
        "2. edit_interaction: {{\"tool\": \"edit_interaction\", \"tool_args\": {\"interaction_id\": int, \"updates\": dict}}}\n"
        "3. summarize_interaction: {{\"tool\": \"summarize_interaction\", \"tool_args\": {\"text\": str}}}\n"
        "4. suggest_followup: {{\"tool\": \"suggest_followup\", \"tool_args\": {\"text\": str}}}\n"
        "5. retrieve_interaction_history: {{\"tool\": \"retrieve_interaction_history\", \"tool_args\": {\"hcp_name\": str}}}\n\n"
        "Return ONLY a JSON object with keys 'tool' and 'tool_args'.\n\n"
        f"User message:\n{text}"
    )
    raw = client.chat(prompt)

    import json

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"tool": "log_interaction", "tool_args": {"input_text": text}}

    tool_name = parsed.get("tool", "log_interaction")
    tool_args = parsed.get("tool_args", {"input_text": text})

    state["intent"] = tool_name
    state["tool_name"] = tool_name
    state["tool_args"] = tool_args
    return state


def _execute_tool(state: AgentState) -> AgentState:
    """Execute the selected tool and store the result."""
    tool_name = state.get("tool_name") or "log_interaction"
    tool = TOOLS_MAP.get(tool_name, log_interaction_tool)
    args = state.get("tool_args") or {}
    # LangChain tools expose .invoke
    result = tool.invoke(args)
    state["result"] = result
    return state


def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("detect_intent", _detect_intent)
    graph.add_node("execute_tool", _execute_tool)

    graph.set_entry_point("detect_intent")
    graph.add_edge("detect_intent", "execute_tool")
    graph.add_edge("execute_tool", END)

    return graph.compile()


AGENT_APP = build_agent()


def run_agent(input_text: str) -> Dict[str, Any]:
    """Public helper to run the LangGraph agent with plain text input."""
    initial_state: AgentState = {"input_text": input_text}
    final_state = AGENT_APP.invoke(initial_state)
    return final_state.get("result", {})

