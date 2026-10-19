# Architecture Decision Records (ADRs)

---

## ADR-001: Separation of Flow Orchestrator and Multi-Agent Crew
* **Date**: 2026-10-19
* **Status**: Accepted
* **Context**: Need reliable control over validation, data retrieval, and budget calculation without risking LLM hallucinations or tool loop traps.
* **Decision**: Adopt **CrewAI Flow** for application lifecycle transitions and keep **Crew** strictly for multi-agent synthesis.
* **Consequences**: Programmatic reliability for business rules, predictable token consumption, and simplified debugging.

---

## ADR-002: Dual Transit Discovery (RailRadar API + Agent Web Search)
* **Date**: 2026-10-19
* **Status**: Accepted
* **Context**: Developer RailRadar API has a strict 20-hit quota limit; hardcoding schedules is unacceptable, while pure web scraping can be brittle.
* **Decision**: Implement persistent atomic disk caching (`.railradar_cache.json`) for RailRadar API hits and provide seamless fallback to live web search (`DDGS`).
* **Consequences**: Zero API hit exhaustion while providing verified schedules and exact geographical coordinates for OpenStreetMap visualization.

---

## ADR-003: Model Context Protocol (MCP) Standardization
* **Date**: 2026-10-19
* **Status**: Accepted
* **Context**: Need standard tool-calling interface that avoids proprietary lock-in.
* **Decision**: Built a standalone MCP server using official `mcp` SDK exposing `search_trains`, `search_buses`, and `get_weather`.
* **Consequences**: Enables decoupling of tools and allows external clients to interact with platform services seamlessly.
