from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.config import settings
from app.rag import rag
from app.tool import calculate_trip_cost, format_response, get_weather, parse_user_query

logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4", api_key=settings.OPENAI_API_KEY, temperature=0.3)


class TravelPlanState(TypedDict):
    user_input: str
    is_travel_related: bool
    rejection_reason: str
    request_mode: str
    parsed_query: dict
    weather_info: dict
    travel_docs: str
    has_rag_context: bool
    rag_source: str
    cost_estimate: dict
    final_plan: str


def _as_text(response: Any) -> str:
    if hasattr(response, "content"):
        return str(response.content).strip()
    return str(response).strip()


def _extract_json_block(text: str) -> dict[str, Any]:
    normalized = text.strip().replace("```json", "").replace("```", "").strip()
    start = normalized.find("{")
    end = normalized.rfind("}")
    if start == -1 or end == -1 or end < start:
        return {}
    try:
        return json.loads(normalized[start : end + 1])
    except json.JSONDecodeError:
        return {}


def _safe_int(value: Any, default: int) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_input_node(state: dict) -> dict:
    """Normalize inbound payloads into the graph's expected user_input field."""
    if "user_input" in state and state["user_input"]:
        user_input = state["user_input"]
    elif isinstance(state.get("input"), dict) and state["input"].get("message"):
        user_input = state["input"]["message"]
    elif state.get("message"):
        user_input = state["message"]
    else:
        user_input = state.get("input", "")
    return {"user_input": str(user_input)}


def validation_node(state: TravelPlanState) -> dict:
    """Check travel intent and extract budget/destination/day/person preferences from user input."""
    user_input = state["user_input"]
    logger.info("[validation_node] Analyzing request: %s", user_input)

    fallback = parse_user_query(user_input)
    lowered = user_input.lower()
    recommendation_signals = {"recommend", "suggest", "idea", "ideas", "where should", "best place"}
    fallback_mode = "recommendation" if any(signal in lowered for signal in recommendation_signals) else "plan"

    previous_parsed = state.get("parsed_query", {})

    extraction_prompt = f"""
You are an information extractor for travel planning requests.
You are provided with the user's current input and their previous travel parameters (if any).
Update the parameters based on the new user input. If a parameter is not mentioned in the new input, keep its previous value.
If there are no previous values, use null for missing information.

Previous parameters:
{json.dumps(previous_parsed, indent=2)}

Return strict JSON with exactly these keys:
{{
  "is_travel_related": boolean,
  "destination": string | null,
  "days": integer | null,
  "budget": integer | null,
  "people": integer | null,
  "accommodation_type": string | null,
  "request_mode": "plan" | "recommendation" | null
}}

Rules:
- is_travel_related must be true only for travel-related requests.
- destination should be the place user wants to visit.
- days is trip length.
- budget is total budget in USD-equivalent numeric value when present.
- people is traveler count.
- accommodation_type should be one of: budget, mid-range, luxury when inferable.
- request_mode = recommendation when user asks for suggestions, else plan.

User input: {user_input}
"""
    extracted = _extract_json_block(_as_text(llm.invoke(extraction_prompt)))

    travel_keywords = {
        "travel",
        "trip",
        "itinerary",
        "destination",
        "flight",
        "hotel",
        "accommodation",
        "visa",
        "tour",
        "vacation",
        "holiday",
        "backpacking",
        "weather",
        "restaurant",
        "activities",
        "airport",
        "transport",
        "plan",
        "recommend",
    }
    keyword_match = any(keyword in lowered for keyword in travel_keywords)
    is_travel = bool(extracted.get("is_travel_related", False)) or keyword_match

    if not is_travel:
        rejection = (
            "Sorry, I can only help with travel-related requests. "
            "Please ask me about travel planning, destinations, accommodations, weather, or activities."
        )
        return {
            "is_travel_related": False,
            "rejection_reason": rejection,
            "final_plan": rejection,
        }

    parsed = {
        "destination": extracted.get("destination") or previous_parsed.get("destination") or fallback["destination"],
        "days": max(1, _safe_int(extracted.get("days"), previous_parsed.get("days") or fallback["days"])),
        "people": max(1, _safe_int(extracted.get("people"), previous_parsed.get("people") or fallback["people"])),
        "budget": max(0, _safe_int(extracted.get("budget"), previous_parsed.get("budget") or fallback["budget"])),
        "accommodation_type": extracted.get("accommodation_type") or previous_parsed.get("accommodation_type") or fallback["accommodation_type"],
    }
    request_mode = extracted.get("request_mode") or fallback_mode
    logger.info(
        "[validation_node] Travel request parsed: destination=%s, days=%s, budget=%s, people=%s, mode=%s",
        parsed["destination"],
        parsed["days"],
        parsed["budget"],
        parsed["people"],
        request_mode,
    )
    return {
        "is_travel_related": True,
        "parsed_query": parsed,
        "request_mode": request_mode,
    }


def routing_node(state: TravelPlanState) -> Literal["process_request", "reject_request"]:
    return "process_request" if state["is_travel_related"] else "reject_request"


def rag_node(state: TravelPlanState) -> dict:
    """Check Pinecone RAG for destination context, fallback to model knowledge when missing."""
    destination = state["parsed_query"]["destination"]
    query = state["user_input"]
    k = 3
    docs, has_context = rag.retrieve_destination_context(destination=destination, query=query, k=k)
    logger.info("[rag_node] Destination='%s' rag_context=%s", destination, has_context)
    return {
        "travel_docs": docs,
        "has_rag_context": has_context,
        "rag_source": "pinecone" if has_context else "llm_internal",
    }


def weather_node(state: TravelPlanState) -> dict:
    """Fetch weather forecast using destination extracted from user input."""
    destination = state["parsed_query"]["destination"]
    days = state["parsed_query"]["days"]
    today = datetime.now()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
    weather = get_weather(destination, start_date, end_date)
    return {"weather_info": weather}


def calculation_node(state: TravelPlanState) -> dict:
    """Calculate trip costs for extracted destination and trip info."""
    parsed = state["parsed_query"]
    cost = calculate_trip_cost(
        destination=parsed["destination"],
        num_days=parsed["days"],
        num_people=parsed["people"],
        accommodation_type=parsed["accommodation_type"],
    )
    return {"cost_estimate": cost}


def synthesis_node(state: TravelPlanState) -> dict:
    """Build final answer using parsed input + optional Pinecone context + weather + cost."""
    rag_context = (
        state["travel_docs"]
        if state.get("has_rag_context")
        else "No destination-specific RAG context found. Use your own travel knowledge."
    )
    prompt = f"""You are a travel assistant.
Only answer travel topics.
Use Pinecone RAG context when present; otherwise use your own travel knowledge.
Do not ask the user to upload documents.

Destination: {state['parsed_query']['destination']}
Days: {state['parsed_query']['days']}
People: {state['parsed_query']['people']}
User Budget: {state['parsed_query']['budget']}
Request Mode: {state.get('request_mode', 'plan')}
RAG Source: {state.get('rag_source', 'llm_internal')}

Budget Breakdown:
{json.dumps(state['cost_estimate'], indent=2)}

RAG Context:
{rag_context}

Weather Status: {state['weather_info'].get('status', 'unknown')}

If Request Mode is "recommendation", provide destination/activity/hotel/food recommendations.
If Request Mode is "plan", provide a day-by-day itinerary.
Always include concise budget and packing guidance."""
    response = llm.invoke(prompt)
    plan_text = _as_text(response)

    formatted_plan = format_response(
        {
            "destination": state["parsed_query"]["destination"],
            "days": state["parsed_query"]["days"],
            "cost": state["cost_estimate"],
            "weather": state["weather_info"],
            "documents": state["travel_docs"][:500],
        }
    )
    final_answer = f"{formatted_plan}\n\n{plan_text}"
    return {"final_plan": final_answer}


def reject_node(state: TravelPlanState) -> dict:
    return {
        "final_plan": "Sorry, I can only help with travel-related requests. Please ask me about travel planning, destinations, accommodations, weather, or activities."
    }


def build_graph():
    workflow = StateGraph(TravelPlanState)
    workflow.add_node("normalize_input", normalize_input_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("weather", weather_node)
    workflow.add_node("calculation", calculation_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("reject", reject_node)

    workflow.add_edge(START, "normalize_input")
    workflow.add_edge("normalize_input", "validation")
    workflow.add_conditional_edges(
        "validation",
        routing_node,
        {
            "process_request": "rag",
            "reject_request": "reject",
        },
    )
    workflow.add_edge("rag", "weather")
    workflow.add_edge("weather", "calculation")
    workflow.add_edge("calculation", "synthesis")
    workflow.add_edge("synthesis", END)
    workflow.add_edge("reject", END)
    return workflow


def compile_graph(*, use_checkpointer: bool = False):
    workflow = build_graph()
    if use_checkpointer:
        return workflow.compile(checkpointer=MemorySaver())
    return workflow.compile()


graph = compile_graph(use_checkpointer=False)
app_graph = compile_graph(use_checkpointer=True)
