"""Standalone LangGraph implementation demonstrating StateGraph, Checkpointing, and Human-in-the-Loop interrupts."""
from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from solo_travel.models.state import UserTravelRequest, TravelStyle
from solo_travel.guardrails.safety import evaluate_travel_request_guardrails
from solo_travel.providers.transport import TransportProvider
from solo_travel.providers.hostels import HostelProvider
from solo_travel.providers.weather import WeatherProvider


class GraphTravelState(TypedDict):
    """LangGraph typed dictionary state."""
    origin: str
    destination: str
    duration_days: int
    budget_inr: float
    travel_style: str
    interests: List[str]
    guardrail_safe: bool
    rejection_reasons: List[str]
    transit_options: List[Dict[str, Any]]
    hostel_options: List[Dict[str, Any]]
    weather_info: Dict[str, Any]
    human_approved: bool
    final_itinerary: Optional[str]


def guardrail_node(state: GraphTravelState) -> Dict[str, Any]:
    """Node 1: Evaluates deterministic guardrails."""
    req = UserTravelRequest(
        origin=state["origin"],
        destination=state["destination"],
        duration_days=state["duration_days"],
        total_budget_inr=state["budget_inr"],
        travel_style=TravelStyle(state["travel_style"]),
        interests=state["interests"]
    )
    res = evaluate_travel_request_guardrails(req)
    return {
        "guardrail_safe": res.is_safe,
        "rejection_reasons": res.rejection_reasons
    }


def research_node(state: GraphTravelState) -> Dict[str, Any]:
    """Node 2: Gathers transport, hostels, and weather data."""
    t_provider = TransportProvider()
    h_provider = HostelProvider()
    w_provider = WeatherProvider()

    transits = t_provider.search(state["origin"], state["destination"])
    hostels = h_provider.search(state["destination"])
    weather = w_provider.search(state["destination"])

    return {
        "transit_options": [t.model_dump() for t in transits[:2]],
        "hostel_options": [h.model_dump() for h in hostels[:2]],
        "weather_info": weather
    }


def human_review_node(state: GraphTravelState) -> Dict[str, Any]:
    """Node 3: Human checkpoint (can be interrupted or approved)."""
    return {"human_approved": True}


def synthesis_node(state: GraphTravelState) -> Dict[str, Any]:
    """Node 4: Produces structured itinerary synthesis."""
    itin = (
        f"# LangGraph Solo Itinerary: {state['origin']} -> {state['destination']}\n"
        f"• Duration: {state['duration_days']} Days | Budget: ₹{state['budget_inr']:,.0f}\n"
        f"• Selected Transit: {state['transit_options'][0]['identifier'] if state['transit_options'] else 'Standard Rail'}\n"
        f"• Recommended Hostel: {state['hostel_options'][0]['name'] if state['hostel_options'] else 'Central Hostel'}\n"
        f"• Weather: {state['weather_info'].get('current_temp_c', 'N/A')}°C\n"
    )
    return {"final_itinerary": itin}


def build_solo_travel_graph(checkpointer: Optional[MemorySaver] = None):
    """Builds and compiles the LangGraph StateGraph."""
    workflow = StateGraph(GraphTravelState)

    workflow.add_node("guardrails", guardrail_node)
    workflow.add_node("research", research_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("synthesis", synthesis_node)

    workflow.add_edge(START, "guardrails")

    def route_guardrails(state: GraphTravelState):
        if not state["guardrail_safe"]:
            return END
        return "research"

    workflow.add_conditional_edges("guardrails", route_guardrails)
    workflow.add_edge("research", "human_review")
    workflow.add_edge("human_review", "synthesis")
    workflow.add_edge("synthesis", END)

    return workflow.compile(checkpointer=checkpointer)
