# 🎒 Autonomous Solo Travel Intelligence Platform

A production-grade, budget-first **Solo Travel Planning Platform** tailored for travelers in India and globally.

Built with **CrewAI Flows**, **Multi-Agent Orchestration**, **Model Context Protocol (MCP)**, **OpenStreetMap**, and **Layered Deterministic Guardrails**.

Powered 100% locally by **Ollama (`llama3.1:8b`, `qwen2.5:7b`)** or Cloud LLMs (**Google Gemini 2.0 Flash**, **Groq**).

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

```
User Input ➔ Deterministic Guardrails ➔ CrewAI Flow (@start / @listen)
                                                 │
                   ┌─────────────────────────────┼────────────────────────────┐
                   ▼                             ▼                            ▼
         [RailRadar / Buses]           [Live Hostel Search]            [Open-Meteo Weather]
                   │                             │                            │
                   └─────────────────────────────┼────────────────────────────┘
                                                 │
                                       [3-Agent CrewAI Team]
                                       • Transit Scout
                                       • Hostel Specialist
                                       • Budget Synthesizer
                                                 │
                                                 ▼
                                     [Deterministic INR Math]
                                                 │
                                                 ▼
                       [Interactive OpenStreetMap & Markdown Plan]
```

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
