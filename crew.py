"""
Core Multi-Agent Orchestrator for Trip Planning.
Demonstrates:
- Multi-Agent Collaboration (Scout -> Guide -> Architect)
- Tool-calling guardrails (preventing infinite search loops)
- Task chaining with context propagation
- Dynamic local LLM selection (Ollama llama3.1 vs qwen2.5)
"""
from typing import Dict, Any, Callable, Optional
from crewai import Agent, Task, Crew, LLM, Process
from tools import search_internet

def create_trip_crew(
    origin: str,
    destination: str,
    duration_days: int,
    budget_level: str,
    interests: str,
    model_name: str = "llama3.1:8b",
    step_callback: Optional[Callable] = None
) -> Crew:
    """
    Constructs a robust 3-agent CrewAI pipeline.
    """
    # 1. Initialize local LLM on Ollama
    local_llm = LLM(
        model=f"ollama/{model_name}",
        base_url="http://localhost:11434",
        temperature=0.4
    )

    # 2. Agent 1: Destination Scout (Analyzes weather, season, vibe, cultural norms)
    scout_agent = Agent(
        role="Destination & Logistics Analyst",
        goal=f"Analyze travel logistics and seasonal context for {destination} originating from {origin}",
        backstory=(
            "You are an international travel consultant. You assess current climate, "
            "best travel windows, transportation modes, and local etiquette. You use search "
            "strictly for current seasonal conditions and provide concise bullet points."
        ),
        tools=[search_internet],
        llm=local_llm,
        max_iter=3,
        step_callback=step_callback,
        verbose=True
    )

    # 3. Agent 2: Local Experience Guide (Attractions, hidden gems, gastronomy)
    guide_agent = Agent(
        role="Local Experience & Gastronomy Specialist",
        goal=f"Curate authentic activities, top attractions, and dining in {destination} tailored to {interests} and {budget_level} budget",
        backstory=(
            "You are a local insider guide. You know where to find authentic food, iconic sights, "
            "and hidden spots while respecting budget constraints. You avoid generic tourist traps."
        ),
        tools=[search_internet],
        llm=local_llm,
        max_iter=4,
        step_callback=step_callback,
        verbose=True
    )

    # 4. Agent 3: Master Itinerary Architect (Synthesizes everything into day-by-day plan)
    architect_agent = Agent(
        role="Master Itinerary Architect",
        goal=f"Synthesize destination research and local guide recommendations into an actionable, realistic {duration_days}-day itinerary",
        backstory=(
            "You are an elite travel planner known for perfectly paced itineraries. You balance "
            "active exploration with relaxation, group geographically close activities to minimize transit, "
            "and provide clear budget breakdowns."
        ),
        tools=[],  # Pure synthesizer: relies on research from previous agents to avoid extra search latency
        llm=local_llm,
        max_iter=3,
        step_callback=step_callback,
        verbose=True
    )

    # ========================== TASKS DEFINITION ==========================

    # Task 1: Destination Context & Logistics
    scout_task = Task(
        description=(
            f"Analyze travel from {origin} to {destination} for a {duration_days}-day trip.\n"
            f"1. Best time to visit and current seasonal weather notes.\n"
            f"2. Primary transit advice from {origin} to {destination}.\n"
            f"3. 2 vital cultural etiquette or safety tips.\n"
            "Guardrail: Execute at most 1 web search if needed, then output your structured brief."
        ),
        expected_output="A structured destination brief with Weather/Season, Transit Advice, and Etiquette/Tips.",
        agent=scout_agent
    )

    # Task 2: Curate Experiences & Dining
    guide_task = Task(
        description=(
            f"Research experiences in {destination} for a {budget_level} budget traveler interested in: {interests}.\n"
            f"1. Select 4-6 top attractions and activities matched to interests.\n"
            f"2. Recommend 3 authentic dining spots (breakfast, lunch, dinner).\n"
            f"3. Highlight 1 off-the-beaten-path hidden gem.\n"
            "Guardrail: Execute at most 2 targeted web searches, then write your complete recommendations."
        ),
        expected_output="A curated guide with Top Attractions, 3 Dining Spots with signature dishes, and 1 Hidden Gem.",
        agent=guide_agent
    )

    # Task 3: Final Master Itinerary (Context chained from Task 1 & 2)
    architect_task = Task(
        description=(
            f"Create a cohesive {duration_days}-day travel itinerary for {destination}.\n"
            f"Traveler Profile: Departing from {origin}, {budget_level} budget, Interests: {interests}.\n\n"
            "Requirements:\n"
            f"- Generate a structured Day-by-Day schedule (Day 1 to Day {duration_days}) broken into Morning, Afternoon, and Evening.\n"
            "- Incorporate the attractions and dining recommended by the Local Guide.\n"
            "- Add estimated daily budget allocation and practical packing advice.\n"
            "- Produce a polished Markdown document ready for the traveler."
        ),
        expected_output="A comprehensive, beautifully formatted Markdown trip itinerary with Day-by-Day sections, Budget estimates, and Packing/Transit notes.",
        agent=architect_agent,
        context=[scout_task, guide_task]  # Multi-Agent Context Injection!
    )

    # 5. Build Sequential Crew
    crew = Crew(
        agents=[scout_agent, guide_agent, architect_agent],
        tasks=[scout_task, guide_task, architect_task],
        process=Process.sequential,
        verbose=True
    )

    return crew
