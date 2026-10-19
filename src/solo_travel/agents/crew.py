"""Multi-agent CrewAI orchestration for Solo Travel Intelligence."""
from typing import Optional, Callable
from crewai import Agent, Task, Crew, Process, LLM
from solo_travel.models.state import UserTravelRequest
from solo_travel.tools.search import search_internet
from solo_travel.tools.providers import search_trains_tool, search_buses_tool, get_weather_tool
from solo_travel.llm.provider import get_llm
from solo_travel.config import LLMProviderType, get_settings


def create_solo_travel_crew(
    request: UserTravelRequest,
    provider: LLMProviderType = LLMProviderType.OLLAMA,
    model_name: Optional[str] = None,
    step_callback: Optional[Callable] = None,
) -> Crew:
    """
    Constructs a decoupled 3-agent CrewAI team:
    1. Logistics & Transit Scout (Equipped with verified train/bus feeds and weather tool)
    2. Hostel & Local Experiences Specialist (Budget stays, food, social safety)
    3. Itinerary & Budget Synthesizer (Pure synthesizer, zero redundant searches)
    """
    settings = get_settings()
    llm: LLM = get_llm(provider=provider, model_name=model_name, settings=settings)

    interests_str = ", ".join(request.interests) if request.interests else "local culture and budget exploration"
    travel_style_str = request.travel_style.value

    # Agent 1: Logistics & Transit Scout
    scout_agent = Agent(
        role="Solo Travel Logistics & Transit Scout",
        goal=(
            f"Identify the most economical transit options and current seasonal context "
            f"from {request.origin} to {request.destination} for a solo traveller."
        ),
        backstory=(
            "You are an expert on economical travel in India and globally. You prioritize "
            "cost-effective trains (e.g. Sleeper/3AC), state buses, and sensible transit routes. "
            "You consult verified train/bus schedules and live weather feeds first before web searching."
        ),
        tools=[search_trains_tool, search_buses_tool, get_weather_tool, search_internet],
        llm=llm,
        max_iter=settings.AGENT_MAX_ITER,
        step_callback=step_callback,
        verbose=True,
    )

    # Agent 2: Hostel & Local Experience Specialist
    guide_agent = Agent(
        role="Hostel & Solo Experience Specialist",
        goal=(
            f"Curate safe, highly-rated social hostels, walking routes, and affordable local food in {request.destination} "
            f"suited for a solo traveler with a {travel_style_str} budget."
        ),
        backstory=(
            "You specialize in solo travel dynamics. You value backpacker hostels with active common areas, "
            "clean dorms (including female dorm options when requested), and cheap local street food / thali spots. "
            "You know how to avoid unsafe or isolated areas."
        ),
        tools=[search_internet],
        llm=llm,
        max_iter=settings.AGENT_MAX_ITER,
        step_callback=step_callback,
        verbose=True,
    )

    # Agent 3: Itinerary & Budget Synthesizer
    synthesizer_agent = Agent(
        role="Solo Itinerary & Budget Synthesizer",
        goal=(
            f"Synthesize transit and hostel research into an actionable, realistic {request.duration_days}-day itinerary "
            f"strictly respecting the total budget of ₹{request.total_budget_inr:,.0f}."
        ),
        backstory=(
            "You are a rigorous travel planner. You group geographically proximate sights to avoid excessive "
            "rickshaw/taxi fares, allocate a contingency fund, and provide a clear, itemized INR budget breakdown."
        ),
        tools=[],  # Pure synthesizer: uses context from prior agents to avoid tool-calling latency
        llm=llm,
        max_iter=settings.AGENT_MAX_ITER,
        step_callback=step_callback,
        verbose=True,
    )

    # Task 1: Transit & Logistics Task
    scout_task = Task(
        description=(
            f"Research travel logistics from {request.origin} to {request.destination}.\n"
            f"Duration: {request.duration_days} days. Total Budget: ₹{request.total_budget_inr:,.0f}.\n"
            f"Preferences: Overnight travel permitted={request.allow_overnight_travel}.\n"
            "Key Requirements:\n"
            "1. Identify the primary budget transit modes (Trains, Buses, or Shared cabs) with estimated fares in INR.\n"
            "2. Note major arrival railway stations or bus terminals.\n"
            "3. Current seasonal weather and vital solo traveler safety advice.\n"
            "Guardrail: Execute at most 1 targeted search if needed, then output your structured brief."
        ),
        expected_output="A structured transit brief with identified routes, terminal stations, estimated INR fares, and safety notes.",
        agent=scout_agent,
    )

    # Task 2: Hostels & Experience Task
    guide_task = Task(
        description=(
            f"Research budget hostels and local experiences in {request.destination} for interests: {interests_str}.\n"
            f"Travel style: {travel_style_str}. Prefer hostels={request.hostel_preference}, "
            f"Require female dorm={request.require_female_dorm}.\n"
            "Key Requirements:\n"
            "1. Recommend 2 specific backpacker hostels (dorm rates in INR/night, neighborhood, social vibe).\n"
            "2. Identify 3-4 affordable attractions grouped by vicinity.\n"
            "3. Highlight 2-3 local food spots (thali, street food hubs, budget cafes).\n"
            "Guardrail: Execute at most 2 targeted searches, then output your findings."
        ),
        expected_output="Curated hostel options with per-night INR rates, neighborhood safety notes, and clustered sights/food.",
        agent=guide_agent,
    )

    # Task 3: Itinerary & Budget Synthesis Task
    synth_task = Task(
        description=(
            f"Create a comprehensive {request.duration_days}-day solo travel plan for {request.destination}.\n"
            f"Origin: {request.origin}. Total Budget: ₹{request.total_budget_inr:,.0f}.\n\n"
            "Deliverables:\n"
            f"- Day-by-Day schedule (Day 1 to Day {request.duration_days}) broken into Morning, Afternoon, Evening.\n"
            "- Selected transit route and arrival instructions.\n"
            "- Selected hostel recommendation and estimated total accommodation cost.\n"
            "- Itemized INR Budget Breakdown: Transit + Accommodation + Food + Activities + Contingency = Total.\n"
            "- Ensure the Total does NOT exceed the user's budget.\n"
            "- Practical Solo Traveler tips (connectivity, safety, local transit hacks)."
        ),
        expected_output="A complete, beautifully formatted Markdown solo travel itinerary with day-by-day plans, budget table, and solo safety notes.",
        agent=synthesizer_agent,
        context=[scout_task, guide_task],
    )

    return Crew(
        agents=[scout_agent, guide_agent, synthesizer_agent],
        tasks=[scout_task, guide_task, synth_task],
        process=Process.sequential,
        verbose=True,
    )
