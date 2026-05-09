from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Any, Literal
from langchain_openai import ChatOpenAI
from app.config import settings
from app.tool import get_weather, calculate_trip_cost, parse_user_query, format_response
from app.rag import rag
from datetime import datetime, timedelta
import json
import logging

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
    cost_estimate: dict
    final_plan: str

def _as_text(response: Any) -> str:
    if hasattr(response, "content"):
        return str(response.content).strip()
    return str(response).strip()

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
    """Check if question is travel-related."""
    logger.info(f"🔍 [validation_node] Checking if travel-related: {state['user_input']}")

    lowered = state["user_input"].lower()
    travel_keywords = {
        "travel", "trip", "itinerary", "destination", "flight", "hotel", "accommodation",
        "visa", "tour", "vacation", "holiday", "backpacking", "weather", "restaurant",
        "activities", "airport", "transport", "plan", "recommend"
    }
    keyword_match = any(keyword in lowered for keyword in travel_keywords)

    validation_prompt = f"""Determine if this question is about travel planning, trip recommendations, or travel information.

Question: {state['user_input']}

Respond with ONLY: "YES" or "NO"

Examples:
- "Plan a trip to Paris" → YES
- "What's the weather in Tokyo?" → YES
- "Best hotels in Bangkok" → YES
- "What's 2+2?" → NO
- "Write me a poem" → NO
- "Tell me a joke" → NO"""

    response = llm.invoke(validation_prompt)
    response_text = _as_text(response).upper()

    is_travel = keyword_match or ("YES" in response_text)
    logger.info(f"✅ [validation_node] Result: {'TRAVEL RELATED' if is_travel else 'NOT TRAVEL RELATED'}")

    if not is_travel:
        rejection = "❌ Sorry, I can only help with travel-related requests. Please ask me about travel planning, destinations, accommodations, weather, or activities."
        return {
            "is_travel_related": False,
            "rejection_reason": rejection,
            "final_plan": rejection,
        }

    return {"is_travel_related": True}

def routing_node(state: TravelPlanState) -> Literal["process_request", "reject_request"]:
    """Route based on validation result."""
    if state["is_travel_related"]:
        logger.info("➡️  [routing] Routing to: process_request")
        return "process_request"
    else:
        logger.info("➡️  [routing] Routing to: reject_request")
        return "reject_request"

def input_node(state: TravelPlanState) -> dict:
    """Parse and validate user input."""
    logger.info(f"🔄 [input_node] Processing: {state['user_input']}")
    parsed = parse_user_query(state["user_input"])
    logger.info(f"✅ [input_node] Parsed: dest={parsed['destination']}, days={parsed['days']}, budget=${parsed['budget']}")
    return {"parsed_query": parsed}

def request_mode_node(state: TravelPlanState) -> dict:
    """Decide whether user asked for recommendation or full plan."""
    lowered = state["user_input"].lower()
    recommendation_signals = {"recommend", "suggest", "idea", "ideas", "where should", "best place"}
    mode = "recommendation" if any(signal in lowered for signal in recommendation_signals) else "plan"
    logger.info(f"✅ [request_mode_node] Mode: {mode}")
    return {"request_mode": mode}

def rag_node(state: TravelPlanState) -> dict:
    """Retrieve travel documents for the destination."""
    logger.info("🔄 [rag_node] Retrieving travel documents...")
    query = state["user_input"]
    destination = state["parsed_query"]["destination"]
    lexical_docs = rag.retrieve(query, k=2)
    destination_docs = rag.retrieve_by_destination(destination)
    docs = f"{destination_docs}\n\n{lexical_docs}".strip()
    logger.info(f"✅ [rag_node] Retrieved {len(docs)} chars of travel guide for {destination}")
    return {"travel_docs": docs}

def weather_node(state: TravelPlanState) -> dict:
    """Fetch weather forecast for destination."""
    logger.info("🔄 [weather_node] Fetching weather forecast...")
    destination = state["parsed_query"]["destination"]
    days = state["parsed_query"]["days"]

    today = datetime.now()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")

    weather = get_weather(destination, start_date, end_date)
    logger.info(f"✅ [weather_node] Weather status: {weather.get('status', 'unknown')}")
    return {"weather_info": weather}

def calculation_node(state: TravelPlanState) -> dict:
    """Calculate trip costs."""
    logger.info("🔄 [calculation_node] Calculating trip costs...")
    parsed = state["parsed_query"]

    cost = calculate_trip_cost(
        destination=parsed["destination"],
        num_days=parsed["days"],
        num_people=parsed["people"],
        accommodation_type=parsed["accommodation_type"]
    )
    logger.info(f"✅ [calculation_node] Total cost: ${cost['total']}")
    return {"cost_estimate": cost}

def synthesis_node(state: TravelPlanState) -> dict:
    """Combine all data into final travel answer."""
    logger.info("🔄 [synthesis_node] Synthesizing final travel answer...")
    prompt = f"""You are a travel assistant.
Only answer travel topics.
Use the travel documents as your primary source and supplement with general travel knowledge.
Do not ask the user to upload documents.

Destination: {state['parsed_query']['destination']}
Days: {state['parsed_query']['days']}
People: {state['parsed_query']['people']}
Request Mode: {state.get('request_mode', 'plan')}

Budget Breakdown:
{json.dumps(state['cost_estimate'], indent=2)}

Travel Tips:
{state['travel_docs']}

Weather Status: {state['weather_info'].get('status', 'unknown')}

If Request Mode is "recommendation", provide destination/activity/hotel/food recommendations.
If Request Mode is "plan", provide a day-by-day itinerary.
Always include concise budget and packing guidance."""

    response = llm.invoke(prompt)
    plan_text = _as_text(response)

    formatted_plan = format_response({
        "destination": state["parsed_query"]["destination"],
        "days": state["parsed_query"]["days"],
        "cost": state["cost_estimate"],
        "weather": state["weather_info"],
        "documents": state["travel_docs"][:500]
    })

    final_answer = f"{formatted_plan}\n\n{plan_text}"
    logger.info(f"✅ [synthesis_node] Final answer created ({len(final_answer)} chars)")
    return {"final_plan": final_answer}

def reject_node(state: TravelPlanState) -> dict:
    """Reject non-travel related requests."""
    logger.info("❌ [reject_node] Rejecting non-travel request")
    return {
        "final_plan": "❌ Sorry, I can only help with travel-related requests. Please ask me about travel planning, destinations, accommodations, weather, or activities."
    }

def build_graph():
    """Build the LangGraph workflow with proper state management."""
    graph = StateGraph(TravelPlanState)

    # Add nodes
    graph.add_node("normalize_input", normalize_input_node)
    graph.add_node("validation", validation_node)
    graph.add_node("input", input_node)
    graph.add_node("request_mode_router", request_mode_node)
    graph.add_node("rag", rag_node)
    graph.add_node("weather", weather_node)
    graph.add_node("calculation", calculation_node)
    graph.add_node("synthesis", synthesis_node)
    graph.add_node("reject", reject_node)

    # Add edges - start by normalizing the inbound payload
    graph.add_edge(START, "normalize_input")
    graph.add_edge("normalize_input", "validation")

    # Conditional routing based on travel-related check
    graph.add_conditional_edges(
        "validation",
        routing_node,
        {
            "process_request": "input",
            "reject_request": "reject"
        }
    )

    # Processing flow for travel requests
    graph.add_edge("input", "request_mode_router")
    graph.add_edge("request_mode_router", "rag")
    graph.add_edge("rag", "weather")
    graph.add_edge("weather", "calculation")
    graph.add_edge("calculation", "synthesis")

    # End nodes
    graph.add_edge("synthesis", END)
    graph.add_edge("reject", END)

    return graph.compile()

graph = build_graph()
