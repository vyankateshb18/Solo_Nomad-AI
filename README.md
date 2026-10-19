## Agents that plan. Nomad that wanders.
**Solo_Nomad x AI — Your AI-Powered Budget Travel Companion**

Solo_Nomad x AI is an agentic AI travel-planning project designed specifically for solo travellers who want to explore more while spending less. Instead of simply generating itineraries, the goal is to find the **most affordable way to reach a destination**, compare multiple travel options, and plan the entire trip within a budget.

Built with **CrewAI Flows, **Multi-Agent Orchestration**, **Model Context Protocol (MCP)**, Python, Streamlit, and Ollama** and **Layered Deterministic Guardrails**, the project uses a multi-agent approach to coordinate travel research and trip planning, with support for integrating cloud-based LLMs alongside locally hosted models.

Powered 100% locally by **Ollama (`llama3.1:8b`, `qwen2.5:7b`)** or Cloud LLMs (**Google Gemini 2.0 Flash**, **Groq**).

### Key Features

- **Budget-First Route Discovery:** Compare trains, buses, and flights by fares, travel time, and total journey cost, prioritizing economical options.
- **Multi-Route Comparison:** Explore different ways to travel between a source and destination to identify practical, cost-effective routes.
- **Social Hostel Discovery:** Find and rank hostels using affordability, traveller reviews, ratings, and social atmosphere.
- **Local Food Discovery:** Discover budget-friendly food spots and authentic local experiences.
- **Tourist Attraction Recommendations:** Explore attractions and activities that fit the traveller's interests and budget.
- **Agentic Trip Planning:** Coordinate specialized AI agents to research destinations, compare transport options, recommend stays, and assemble a day-wise itinerary.
- **Local and Cloud LLM Support:** Use locally hosted models through Ollama, with the option to integrate paid LLM APIs.
- **Accessible Web Interface:** Provide an interactive Streamlit UI for planning and comparing trips, with free-tier hosting as a deployment goal.

### Vision

Make solo travel more accessible by helping travellers spend less on getting there, find the right places to stay, experience local food and culture, and make informed decisions throughout their journey.

**Travel smarter. Spend less. Explore more.**

---
## 🚀 Key Highlights & Portfolio Value

* **Zero-Credential Local Inferencing**: Boots out-of-the-box on local Ollama without requiring any cloud API keys.
* **Deterministic Guardrails & Fast Rejection**: Evaluates prompt injection, shell command exploits, and impossible budget thresholds in `< 5ms` before agent execution.
* **Dual Transit Intelligence**:
  * **RailRadar API** with persistent disk caching to preserve developer API limits.
  * **State Bus Adapters & Live Search** for long-distance overnight sleeper buses.
* **OpenStreetMap & Weather Visualization**:
  * Interactive route line linking origin hub to destination.
  * Real-time weather badge (temperatures & rain probability) via **Open-Meteo**.
* **Official Model Context Protocol (MCP) Server**:
  * Exposes typed tools (`search_trains`, `search_buses`, `get_weather`) using the official Python MCP SDK over `stdio`.
* **State Checkpointing & Resumability**:
  * JSON state persistence enabling Human-in-the-Loop review and revision without re-querying tools.
* **Comparative LangGraph Implementation**:
  * Dedicated standalone module in `src/solo_travel/learning_langgraph/` demonstrating `StateGraph`, `MemorySaver`, and interrupts.

---

## 🛠️ Architecture

<img width="600" height="500" alt="image" src="https://github.com/user-attachments/assets/42dd0c11-9954-4836-a0f9-93d7fd2f6386" />

---

## ⚡ Quick Start

### 1. Prerequisites
Ensure Ollama is running locally:
```bash
ollama pull llama3.1:8b
```
### 2. Run the Streamlit Application
```powershell
cd agentic_trip_planner_v2
$env:PYTHONPATH="src"
.\.venv\Scripts\streamlit.exe run app.py
```
Open your browser at `http://localhost:8501`.
### 3. Run Automated Regression Test Suite
```powershell
cd agentic_trip_planner_v2
$env:PYTHONPATH="src"
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

---
## 📚 Technical Documentation

* [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): Component breakdown, trust boundaries, and data flow.
* [docs/CONCEPTS_AND_INTERVIEW_PREP.md](docs/CONCEPTS_AND_INTERVIEW_PREP.md): In-depth cheat sheet covering CrewAI Flows vs Crews, MCP, Guardrails, and LangGraph trade-offs.
* [docs/DECISIONS.md](docs/DECISIONS.md): Architecture Decision Records (ADRs).
