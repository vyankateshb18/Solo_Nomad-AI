# System Architecture & Technical Specifications

**Solo Travel Intelligence Platform (Budget-First • India & International)**

---

## 1. High-Level Architectural Flow

```mermaid
flowchart TD
    User([Solo Traveller]) --> UI[Streamlit Interactive App]
    UI --> Guardrails[Deterministic Guardrails & Sanitization\n- Regex injection defense\n- Minimum daily INR budget validation]
    
    Guardrails -->|Safe & Feasible| Flow[CrewAI Flow Orchestrator]
    Guardrails -->|Blocked| Alert[Fast UI Alert < 5ms]
    
    subgraph FlowLifecycle [CrewAI Flow Lifecycle]
        State[(Typed SoloTravelState - Pydantic)]
        Step1[@start: validate_and_guard]
        Step2[@listen: retrieve_transit_and_weather]
        Step3[@listen: synthesize_crew_itinerary]
        Step4[@listen: verify_and_finalize_budget]
    end
    
    Flow --> Step1
    Step1 --> Step2
    
    Step2 --> DataProviders[Provider Adapters with TTL Cache]
    subgraph DataProviders
        RailRadar[RailRadar API & IRCTC Tariff Adapter]
        LiveBuses[State Roadways & Bus Portals]
        LiveHostels[Live Backpacker Hostel DDG Search]
        OpenMeteo[Open-Meteo Geocoding & Weather API]
    end
    
    Step2 --> Step3
    Step3 --> CrewTeam[3-Agent CrewAI Sequential Team]
    subgraph CrewTeam
        Agent1[Logistics & Transit Scout\n(max_iter=3, Bounded Tools)]
        Agent2[Hostel & Solo Specialist\n(max_iter=3, Female Dorm Safety)]
        Agent3[Itinerary & Budget Synthesizer\n(Zero tool latency)]
    end
    
    Step3 --> Step4
    Step4 --> VerificationEngine[Deterministic Budget Engine\n- Verifies arithmetic without LLM hallucination\n- Allocates contingency buffer]
    
    VerificationEngine --> HITL[Human Review Checkpoint & Checkpointing]
    HITL --> VisualMap[OpenStreetMap PyDeck Interactive Map]
    HITL --> FinalExport[Markdown Itinerary Download]
```

---

## 2. Component Design & Responsibilities

| Component | Path | Responsibility |
| :--- | :--- | :--- |
| **Config & Environment** | `src/solo_travel/config.py` | `BaseSettings` management. Zero import-time side-effects. Safe offline defaults (Ollama offline by default). |
| **Domain State Models** | `src/solo_travel/models/state.py` | Pydantic v2 schemas: `UserTravelRequest`, `TransportOption`, `HostelOption`, `TripBudgetBreakdown`, `SoloTravelState`. |
| **Input Guardrails** | `src/solo_travel/guardrails/safety.py` | Fast regex matching for prompt injection (`ignore previous instructions`, `developer mode`), string sanitization, and budget floor validation. |
| **Data Providers** | `src/solo_travel/providers/` | Decoupled adapters with TTL in-memory caching and persistent disk caching (to conserve 20-hit RailRadar API limit). |
| **MCP Server** | `src/solo_travel/mcp/` | Model Context Protocol server exposing `search_trains`, `search_buses`, `get_weather` over stdio transport. |
| **Flow Orchestrator** | `src/solo_travel/flow/solo_flow.py` | CrewAI Flow controlling the end-to-end lifecycle with typed state transitions. |
| **Spatial Visualization** | `src/solo_travel/maps/osm.py` | Interactive OpenStreetMap route rendering with origin/destination hubs and live weather markers. |
| **LangGraph Comparative** | `src/solo_travel/learning_langgraph/` | Standalone learning module implementing `StateGraph` and checkpointing. |
